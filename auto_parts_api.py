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
    return {k:x[k] for k in ("id","name","description","market","quick","sold","soldAt","photo") if k in x}

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
                    import calendar
                    now=datetime.now(timezone.utc)
                    y,m=(now.year-1,12) if now.month==1 else (now.year,now.month-1)
                    cutoff=now.replace(year=y,month=m,day=min(now.day,calendar.monthrange(y,m)[1])).timestamp()*1000
                    items=[public_item(x) for x in items if not x.get("sold") or x.get("soldAt",0)>=cutoff]
                reply(h,200,{"items":items})
            elif re.fullmatch(r"/api/image/[0-9a-f]{64}",path):
                item=store.get_image(path.rsplit("/",1)[1])
                if not item: reply(h,404,{"error":"Not found"})
                else: h.send(200,item[1],item[0])
            else: reply(h,404,{"error":"Not found"})
        elif h.command=="POST":
            origin=h.headers.get("Origin","")
            if origin!="https://tazeris-auto-parts.onrender.com":
                reply(h,403,{"error":"Invalid origin"});return True
            if path=="/api/login":
                # Persistent rate limiting must be configured before exposing login.
                reply(h,503,{"error":"Login not enabled until rate limiting is configured"})
            elif not admin(h): reply(h,401,{"error":"Unauthorized"})
            elif path=="/api/logout": reply(h,200,{"ok":True},auth.clear_cookie())
            else: reply(h,404,{"error":"Not found"})
        else: reply(h,405,{"error":"Method not allowed"})
    except (ValueError,TypeError,KeyError): reply(h,400,{"error":"Invalid request"})
    except Exception: reply(h,503,{"error":"Service unavailable"})
    return True
