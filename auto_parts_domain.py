"""Pure inventory rules; no credentials or storage side effects."""
from datetime import datetime, timezone, timedelta
from calendar import monthrange
from decimal import Decimal, InvalidOperation

def money(value):
    try:
        d = Decimal(str(value))
        if not d.is_finite() or d < 0 or d > 1000000:
            raise ValueError("Neteisinga kaina")
        return int(d.quantize(Decimal("0.01")) * 100)
    except (InvalidOperation, TypeError):
        raise ValueError("Neteisinga kaina") from None

def month_ago(now, months):
    year, month = divmod(now.year * 12 + now.month - 1 - months, 12)
    return now.replace(year=year, month=month+1, day=min(now.day, monthrange(year, month+1)[1]))

def timestamp(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Laiko zona privaloma")
    return dt.astimezone(timezone.utc)

def public_visible(item, now):
    if item.get("status") == "available":
        return True
    if item.get("status") != "sold" or not item.get("sold_at"):
        return False
    sold = timestamp(item["sold_at"])
    return month_ago(now, 1) <= sold <= now

def sales_report(items, period, now):
    start = now - timedelta(days=7) if period == "7d" else month_ago(now, {"1m":1,"3m":3,"6m":6,"12m":12}[period])
    rows = [i for i in items if i.get("status") == "sold" and i.get("sold_at") and start <= timestamp(i["sold_at"]) <= now]
    return {"count":len(rows), "revenue_cents":sum(i["actual_price_cents"] for i in rows), "start":start.isoformat(), "end":now.isoformat()}

def validate_valuation(market, quick, sources):
    m, q = money(market), money(quick)
    if not 0 < q <= m:
        raise ValueError("Neteisingas rinkos ir greito pardavimo kainų santykis")
    if not isinstance(sources, list) or not 2 <= len(sources) <= 50:
        raise ValueError("Reikia 2–50 kainų šaltinių")
    from urllib.parse import urlsplit
    urls = set()
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("url"), str):
            raise ValueError("Netinkamas kainos šaltinis")
        url = source["url"]
        if len(url) > 2048 or any(ord(ch) < 32 for ch in url):
            raise ValueError("Netinkamas šaltinio adresas")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Šaltiniui būtinas HTTPS adresas")
        price = money(source.get("price"))
        if price <= 0:
            raise ValueError("Šaltinyje nenurodyta tinkama kaina")
        urls.add(url)
    if len(urls) < 2:
        raise ValueError("Reikia bent dviejų skirtingų kainų šaltinių")
    return m, q
