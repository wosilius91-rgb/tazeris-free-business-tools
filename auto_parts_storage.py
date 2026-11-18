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
    return key

def update_item(key, payload, revision):
    with connection() as conn:
        row = conn.execute("UPDATE auto_parts_inventory SET payload=%s::jsonb, revision=revision+1 WHERE id=%s AND revision=%s RETURNING revision", (json.dumps(payload,ensure_ascii=False),key,revision)).fetchone()
        if not row:
            raise ValueError("Missing item or conflicting revision")
    return row[0]

def list_items():
    with connection() as conn:
        rows = conn.execute("SELECT id,payload,revision FROM auto_parts_inventory ORDER BY created_at DESC").fetchall()
    return [dict(payload,id=str(key),revision=revision) for key,payload,revision in rows]
