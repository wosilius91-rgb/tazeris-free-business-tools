"""Authenticated inventory HTTP API; fail closed when configuration is absent."""
import json, base64, re, time
from http.cookies import SimpleCookie
from urllib.parse import urlparse
import auto_parts_auth as auth
import auto_parts_storage as store

def reply(h, status, obj, cookie=None):
    data=json.dumps(obj,ensure_ascii=False).encode()
    h.send_response(status)
    h.send_header("Content-Type","application/json; charset=utf-8")
    h.send_header("Cache-Control","no-store")
    h.send_header("X-Content-Type-Options","nosniff")
    if cookie: h.send_header("Set-Cookie",cookie)
    h.send_header("Content-Length",str(len(data)))
    h.end_headers()
    h.wfile.write(data)

def admin(h):
    try:
        c=SimpleCookie(h.headers.get("Cookie",""))
        return auth.valid_session(c["auto_parts_session"].value)
    except Exception: return False

def body(h):
    if h.headers.get("Content-Type","").split(";")[0]!="application/json": raise ValueError("JSON required")
    n=int(h.headers.get("Content-Length","0"))
    if not 0<n<=12*1024*1024: raise ValueError("Invalid body size")
    return json.loads(h.rfile.read(n))

def public_item(x):
    return {k:x[k] for k in ("id","name","description","market","quick","status","sold_at","photo") if k in x}

def handle(h):
    path=urlparse(h.path).path
    if not path.startswith("/api/"): return False
    try:
        if h.command=="GET":
            if path=="/api/session": reply(h,200,{"admin":admin(h)})
            elif path=="/api/items":
                store.initialize()
                items=store.list_items()
                if not admin(h):
                    from datetime import datetime, timezone
                    from auto_parts_domain import public_visible
                    now=datetime.now(timezone.utc)
                    items=[public_item(x) for x in items if public_visible(x,now)]
                reply(h,200,{"items":items})
            elif re.fullmatch(r"/api/image/[0-9a-f]{64}",path):
                item=store.get_image(path.rsplit("/",1)[1])
                if not item: reply(h,404,{"error":"Not found"})
                else: h.send(200,item[1],item[0])
            elif path=="/api/report":
                if not admin(h): reply(h,401,{"error":"Unauthorized"})
                else:
                    from urllib.parse import parse_qs
                    from datetime import datetime, timezone
                    from auto_parts_domain import sales_report
                    period=parse_qs(urlparse(h.path).query).get("period",["7d"])[0]
                    if period not in ("7d","1m","3m","6m","12m"): raise ValueError("Invalid period")
                    store.initialize()
                    reply(h,200,sales_report(store.list_items(),period,datetime.now(timezone.utc)))
            else: reply(h,404,{"error":"Not found"})
        elif h.command=="POST":
            origin=h.headers.get("Origin","")
            if origin!="https://tazeris-auto-parts.onrender.com":
                reply(h,403,{"error":"Invalid origin"});return True
            if path=="/api/login":
                credentials=body(h)
                if not store.reserve_login_attempt():
                    reply(h,429,{"error":"Per daug bandymų. Bandykite vėliau."})
                elif not auth.verify_password(credentials.get("password")):
                    reply(h,401,{"error":"Neteisingas slaptažodis"})
                else:
                    reply(h,200,{"ok":True},auth.session_cookie(auth.issue_session()))
            elif not admin(h): reply(h,401,{"error":"Unauthorized"})
            elif path=="/api/logout": reply(h,200,{"ok":True},auth.clear_cookie())
            elif path=="/api/upload":
                data=body(h)
                raw=base64.b64decode(data["data"],validate=True)
                store.initialize()
                key=store.put_image(raw,data["mime"])
                reply(h,201,{"photo":"/api/image/"+key})
            elif path=="/api/items":
                from auto_parts_domain import validate_valuation
                data=body(h)
                name=data["name"].strip()
                description=data["description"].strip()
                photo=data["photo"]
                sources=data["sources"]
                if not name or len(name)>200 or not description or len(description)>10000: raise ValueError("Invalid description")
                if not re.fullmatch(r"/api/image/[0-9a-f]{64}",photo): raise ValueError("Invalid photo")
                if not store.get_image(photo.rsplit("/",1)[1]): raise ValueError("Missing photo")
                market,quick=validate_valuation(data["market"],data["quick"],sources)
                payload=dict(name=name,description=description,photo=photo,market=market/100,quick=quick/100,sources=sources,status="available")
                reply(h,201,{"id":store.insert_item(payload)})
            elif re.fullmatch(r"/api/items/[0-9a-f-]{36}/sell",path):
                from auto_parts_domain import money
                from datetime import datetime, timezone
                data=body(h)
                key=path.split("/")[3]
                item=next((x for x in store.list_items() if x["id"]==key),None)
                if not item: reply(h,404,{"error":"Not found"})
                elif item["status"]!="available" or item["revision"]!=data["revision"]: reply(h,409,{"error":"Conflict"})
                else:
                    revision=item.pop("revision")
                    item.pop("id")
                    item.update(status="sold",sold_at=datetime.now(timezone.utc).isoformat(),actual_price_cents=money(data["actual_price"]))
                    reply(h,200,{"revision":store.update_item(key,item,revision)})
            else: reply(h,404,{"error":"Not found"})
        else: reply(h,405,{"error":"Method not allowed"})
    except (ValueError,TypeError,KeyError): reply(h,400,{"error":"Invalid request"})
    except Exception: reply(h,503,{"error":"Service unavailable"})
    return True
