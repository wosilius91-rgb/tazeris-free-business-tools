import os,json,re
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from ddgs import DDGS
import auto_parts_api
class Handler(BaseHTTPRequestHandler):
 def send(self,status,data,kind):
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  if not auto_parts_api.handle(self):self.send(404,b'Not found','text/plain')
 def do_GET(self):
  if auto_parts_api.handle(self):return
  p=urlparse(self.path)
  if p.path=='/':
   with open('auto_parts.html','rb') as f:self.send(200,f.read(),'text/html; charset=utf-8')
  elif p.path=='/auto-parts-workshop.webp':
   with open(os.path.join(os.path.dirname(__file__),'auto-parts-workshop.webp'),'rb') as f:
    self.send(200,f.read(),'image/webp')
  elif p.path=='/prices':
   # Price research is an administrator operation; do not expose costly searches publicly.
   if not auto_parts_api.admin(self):
    self.send(401,b'{"error":"Unauthorized"}','application/json');return
   q=parse_qs(p.query).get('q',[''])[0].strip()[:200]
   if len(q)<3:
    self.send(400,b'{"error":"Search query too short"}','application/json');return
   out=[];seen=set()
   # Reject obviously unrelated search hits; snippets remain unverified evidence.
   tokens=[t for t in re.findall(r'[\w-]+',q.casefold()) if len(t)>=3]
   identifiers=[t for t in tokens if any(c.isdigit() for c in t)]
   try:
    if q:
     results=[]; failures=[]
     def lookup(request):
      query,region=request
      try:return DDGS(timeout=8).text(query,region=region,max_results=15)
      except Exception as e:
       failures.append(type(e).__name__);return []
     with ThreadPoolExecutor(max_workers=4) as pool:
      for batch in pool.map(lookup,[(q+' naudota detalė kaina €','lt-lt'),(q+' naudotos autodetalės parduoda €','lt-lt'),(q+' used car part price EUR','wt-wt'),(q+' gebraucht Ersatzteil EUR','de-de')]):results.extend(batch)
     for x in results:
      url=x.get('href','');title=x.get('title','');body=x.get('body','')
      if url in seen or urlparse(url).scheme != 'https':continue
      searchable=(title+' '+body).casefold()
      if identifiers and not any(t in searchable for t in identifiers):continue
      if tokens and sum(t in searchable for t in tokens)<min(2,len(tokens)):continue
      matches=re.findall(r'(?:€\s*(\d+(?:[.,]\d{1,2})?)|(\d+(?:[.,]\d{1,2})?)\s*(?:€|EUR\b))',title+' '+body,re.I)
      vals={float((a or b).replace(',','.')) for a,b in matches}
      vals={v for v in vals if 1<=v<=10000}
      if len(vals)==1:
       v=next(iter(vals))
       if 1<=v<=10000:out.append(dict(price=v,url=url,title=title,verified=False,source='search_snippet'));seen.add(url)
    out.sort(key=lambda x:x['price'])
    if q and not results and failures:
     self.send(503,json.dumps({'error':'Paieškos šaltiniai laikinai nepasiekiami','prices':[]}).encode(),'application/json');return
    self.send(200,json.dumps({'prices':out,'verification':'unverified_search_snippets','notice':'Kainos rastos paieškos ištraukose; originalūs skelbimai nepatikrinti. Nevertinti kaip patvirtintų rinkos kainų.'}).encode(),'application/json')
   except Exception:self.send(503,b'{"error":"Paieska laikinai nepasiekiama","prices":[]}','application/json')
  else:self.send(404,b'Not found','text/plain')
if __name__=='__main__':
 ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','10000'))),Handler).serve_forever()
