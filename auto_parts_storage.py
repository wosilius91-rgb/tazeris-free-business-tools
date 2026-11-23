"""Durable inventory storage; never silently falls back to ephemeral disk."""
import os
import json
import uuid
import hashlib
from contextlib import contextmanager

MAX_IMAGE = 8 * 1024 * 1024

@contextmanager
def connection():
    import psycopg
    url = os.environ.get("AUTO_PARTS_DATABASE_URL")
    if not url:
        raise RuntimeError("Durable database is not configured")
    with psycopg.connect(url, connect_timeout=5) as conn:
        yield conn

def initialize():
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS auto_parts_inventory (
            id uuid PRIMARY KEY, payload jsonb NOT NULL,
            revision bigint NOT NULL DEFAULT 1,
            created_at timestamptz NOT NULL DEFAULT now())""")
        conn.execute("""CREATE TABLE IF NOT EXISTS auto_parts_images (
            id text PRIMARY KEY, mime text NOT NULL, data bytea NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now())""")

def put_image(data, mime):
    if not isinstance(data, bytes) or not 0 < len(data) <= MAX_IMAGE:
        raise ValueError("Invalid image size")
    signatures = {
        "image/jpeg": data.startswith(b"\xff\xd8\xff"),
        "image/png": data.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": data.startswith(b"RIFF") and data[8:12] == b"WEBP",
    }
    if not signatures.get(mime, False):
        raise ValueError("Unsupported image")
    key = hashlib.sha256(data).hexdigest()
    with connection() as conn:
        conn.execute("INSERT INTO auto_parts_images (id,mime,data) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", (key,mime,data))
    return key

def get_image(key):
    with connection() as conn:
        row = conn.execute("SELECT mime,data FROM auto_parts_images WHERE id=%s", (key,)).fetchone()
    return (row[0], bytes(row[1])) if row else None

def insert_item(payload):
    key = str(uuid.uuid4())
    with connection() as conn:
        conn.execute("INSERT INTO auto_parts_inventory (id,payload) VALUES (%s,%s::jsonb)", (key,json.dumps(payload,ensure_ascii=False)))
        # Persist publication intentions atomically; never post without a verified connector.
        from auto_parts_domain import money
        import auto_parts_publication
        quick_cents = money(payload["quick"])
        if payload.get("status") == "available" and quick_cents > 0:
            for platform in auto_parts_publication.PLATFORMS:
                auto_parts_publication.record_blocked(conn, key, platform, "publish", quick_cents)
    return key

def update_item(key, payload, revision):
    with connection() as conn:
        row = conn.execute("UPDATE auto_parts_inventory SET payload=%s::jsonb, revision=revision+1 WHERE id=%s AND revision=%s RETURNING revision", (json.dumps(payload,ensure_ascii=False),key,revision)).fetchone()
        if not row:
            raise ValueError("Missing item or conflicting revision")
        # Record blocked price-sync intents atomically; never claim remote updates.
        if payload.get("status") == "available":
            from auto_parts_domain import money
            import auto_parts_publication
            auto_parts_publication.record_price_update_intents(conn, key, money(payload["quick"]))
        # Record closure intents atomically with sale; no external closure is claimed.
        if payload.get("status") == "sold":
            import auto_parts_publication
            auto_parts_publication.record_sale_closures(conn, key)
    return row[0]

def list_items():
    with connection() as conn:
        rows = conn.execute("SELECT id,payload,revision FROM auto_parts_inventory ORDER BY created_at DESC").fetchall()
    return [dict(payload,id=str(key),revision=revision) for key,payload,revision in rows]


def reserve_login_attempt(client_address):
    """Persistent per-client throttle; never trust spoofable forwarded headers."""
    if not isinstance(client_address, str) or len(client_address) > 128:
        return False
    # Hash the address to avoid retaining raw client IPs.
    fingerprint = hashlib.sha256(client_address.encode("utf-8")).hexdigest()
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS auto_parts_login_throttle_v2 (
            bucket bigint NOT NULL, fingerprint text NOT NULL,
            attempts integer NOT NULL,
            PRIMARY KEY (bucket, fingerprint))""")
        conn.execute("""DELETE FROM auto_parts_login_throttle_v2
            WHERE bucket < floor(extract(epoch from now()) / 900)::bigint - 1""")
        row = conn.execute("""INSERT INTO auto_parts_login_throttle_v2 (bucket, fingerprint, attempts)
            VALUES (floor(extract(epoch from now()) / 900)::bigint, %s, 1)
            ON CONFLICT (bucket, fingerprint) DO UPDATE
            SET attempts=auto_parts_login_throttle_v2.attempts+1
            WHERE auto_parts_login_throttle_v2.attempts < 5
            RETURNING attempts""", (fingerprint,)).fetchone()
        return row is not None
