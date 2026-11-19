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
  elif p.path=='/prices':
   q=parse_qs(p.query).get('q',[''])[0][:200]
   out=[];seen=set()
   try:
    if q:
     results=[]; failures=[]
     def lookup(query):
      try:return DDGS(timeout=8).text(query,region='wt-wt',max_results=15)
      except Exception as e:
       failures.append(type(e).__name__);return []
     with ThreadPoolExecutor(max_workers=4) as pool:
      for batch in pool.map(lookup,[q+' used car part price EUR',q+' naudota detalė kaina €',q+' spare part €',q+' gebraucht Ersatzteil EUR']):results.extend(batch)
     for x in results:
      url=x.get('href','');title=x.get('title','');body=x.get('body','')
      if url in seen or urlparse(url).scheme not in ('http','https'):continue
      matches=re.findall(r'(?:€\s*(\d+(?:[.,]\d{1,2})?)|(\d+(?:[.,]\d{1,2})?)\s*(?:€|EUR\b))',title+' '+body,re.I)
      vals={float((a or b).replace(',','.')) for a,b in matches}
      vals={v for v in vals if 1<=v<=10000}
      if len(vals)==1:
       v=next(iter(vals))
       if 1<=v<=10000:out.append(dict(price=v,url=url,title=title));seen.add(url)
    out.sort(key=lambda x:x['price'])
    if q and not results and failures:
     self.send(503,json.dumps({'error':'Paieškos šaltiniai laikinai nepasiekiami','prices':[]}).encode(),'application/json');return
    self.send(200,json.dumps({'prices':out}).encode(),'application/json')
   except Exception:self.send(503,b'{"error":"Paieska laikinai nepasiekiama","prices":[]}','application/json')
  else:self.send(404,b'Not found','text/plain')
if __name__=='__main__':
 ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','10000'))),Handler).serve_forever()
