"""Safe outbound listing ledger. No unsupported platform posting is performed.

A connector must be explicitly registered and tested before any publish/update/close.
The ledger uses the existing durable PostgreSQL database, never local files.
"""
from datetime import datetime, timezone

SUPPORTED_ACTIONS = ("publish", "update", "close")
PLATFORMS = ("skelbiu_lt", "facebook_marketplace")
# Neither platform is enabled without a documented authorized write integration.
ENABLED_CONNECTORS = frozenset()

def validate_job(platform, action, quick_price_cents):
    if platform not in PLATFORMS:
        raise ValueError("Unknown platform")
    if action not in SUPPORTED_ACTIONS:
        raise ValueError("Unknown action")
    if type(quick_price_cents) is not int or quick_price_cents < 0:
        raise ValueError("Invalid quick sale price")
    if platform not in ENABLED_CONNECTORS:
        raise RuntimeError("Authorized connector not configured or verified")
    return True

def initialize(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS auto_parts_external_listings (
        inventory_id uuid NOT NULL REFERENCES auto_parts_inventory(id),
        platform text NOT NULL,
        external_id text,
        external_url text,
        status text NOT NULL DEFAULT 'not_connected',
        last_price_cents bigint,
        last_error text,
        updated_at timestamptz NOT NULL DEFAULT now(),
        PRIMARY KEY (inventory_id, platform),
        CHECK (platform IN ('skelbiu_lt','facebook_marketplace'))
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS auto_parts_listing_jobs (
        id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        inventory_id uuid NOT NULL REFERENCES auto_parts_inventory(id),
        platform text NOT NULL,
        action text NOT NULL,
        price_cents bigint NOT NULL,
        status text NOT NULL DEFAULT 'blocked',
        attempts integer NOT NULL DEFAULT 0,
        last_error text,
        created_at timestamptz NOT NULL DEFAULT now(),
        UNIQUE (inventory_id, platform, action, price_cents),
        CHECK (action IN ('publish','update','close'))
    )""")

def record_blocked(conn, inventory_id, platform, action, quick_price_cents):
    """Record intent for administrator visibility; never pretend it was posted."""
    if platform not in PLATFORMS or action not in SUPPORTED_ACTIONS:
        raise ValueError("Invalid platform/action")
    if type(quick_price_cents) is not int or quick_price_cents < 0:
        raise ValueError("Invalid price")
    initialize(conn)
    conn.execute("""INSERT INTO auto_parts_listing_jobs
        (inventory_id,platform,action,price_cents,status,last_error)
        VALUES (%s,%s,%s,%s,'blocked','No authorized verified connector')
        ON CONFLICT (inventory_id,platform,action,price_cents) DO NOTHING""",
        (inventory_id,platform,action,quick_price_cents))

def record_sale_closures(conn, inventory_id):
    """Queue blocked closure intents only for existing external listings.

    This does NOT claim that an external listing was closed.
    """
    initialize(conn)
    rows = conn.execute("""SELECT platform, COALESCE(last_price_cents,0)
        FROM auto_parts_external_listings
        WHERE inventory_id=%s AND external_id IS NOT NULL
          AND status NOT IN ('closed','confirmed_closed')""",
        (inventory_id,)).fetchall()
    for platform, price in rows:
        record_blocked(conn, inventory_id, platform, "close", int(price))
    return len(rows)


def listing_status(conn, inventory_id):
    """Read-only administrative view of external publication and closure state.

    A queued or blocked closure must never be presented as a confirmed closure.
    """
    initialize(conn)
    listings = conn.execute("""SELECT platform, external_id, external_url, status,
        last_price_cents, last_error, updated_at
        FROM auto_parts_external_listings WHERE inventory_id=%s ORDER BY platform""",
        (inventory_id,)).fetchall()
    jobs = conn.execute("""SELECT platform, action, price_cents, status, attempts,
        last_error, created_at FROM auto_parts_listing_jobs
        WHERE inventory_id=%s ORDER BY created_at DESC, id DESC LIMIT 100""",
        (inventory_id,)).fetchall()
    return {
        "listings": [dict(platform=p, external_id=eid, external_url=url,
            status=status, last_price_cents=price, last_error=error,
            updated_at=updated.isoformat() if updated else None)
            for p,eid,url,status,price,error,updated in listings],
        "jobs": [dict(platform=p, action=a, price_cents=price,
            status=status, attempts=attempts, last_error=error,
            created_at=created.isoformat() if created else None)
            for p,a,price,status,attempts,error,created in jobs],
        "connectors": {platform: ("enabled" if platform in ENABLED_CONNECTORS
            else "not_connected") for platform in PLATFORMS},
    }

def record_price_update_intents(conn, inventory_id, quick_price_cents):
    """Record blocked update requests for existing external listings.

    No platform request is sent unless an authorized connector is added later.
    Only the inventory quick-sale price is used.
    """
    if type(quick_price_cents) is not int or quick_price_cents <= 0:
        raise ValueError("Invalid quick sale price")
    initialize(conn)
    rows = conn.execute("""SELECT platform FROM auto_parts_external_listings
        WHERE inventory_id=%s AND external_id IS NOT NULL
          AND status IN ('active','published')
          AND last_price_cents IS DISTINCT FROM %s""",
        (inventory_id, quick_price_cents)).fetchall()
    for (platform,) in rows:
        record_blocked(conn, inventory_id, platform, "update", quick_price_cents)
    return len(rows)
