import os,json,re
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from ddgs import DDGS
class Handler(BaseHTTPRequestHandler):
 def send(self,status,data,kind):
  self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_GET(self):
  p=urlparse(self.path)
  if p.path=='/':
   with open('auto_parts.html','rb') as f:self.send(200,f.read(),'text/html; charset=utf-8')
  elif p.path=='/prices':
   q=parse_qs(p.query).get('q',[''])[0][:200]
   out=[];seen=set()
   try:
    if q:
     results=[]
     for query in [q+' used car part price EUR',q+' naudota detalė kaina €',q+' spare part €',q+' gebraucht Ersatzteil EUR']:
      try:results.extend(DDGS(timeout=10).text(query,region='lt-lt',max_results=20))
      except Exception:continue
     for x in results:
      url=x.get('href','');title=x.get('title','');body=x.get('body','')
      if url in seen or urlparse(url).scheme not in ('http','https'):continue
      matches=re.findall(r'(?:€\s*(\d+(?:[.,]\d{1,2})?)|(\d+(?:[.,]\d{1,2})?)\s*(?:€|EUR\b))',title+' '+body,re.I)
      vals={float((a or b).replace(',','.')) for a,b in matches}
      if vals:
       v=min(vals)
       if 1<=v<=10000:out.append(dict(price=v,url=url,title=title));seen.add(url)
    out.sort(key=lambda x:x['price'])
    self.send(200,json.dumps({'prices':out}).encode(),'application/json')
   except Exception:self.send(503,b'{"error":"Paieska laikinai nepasiekiama","prices":[]}','application/json')
  else:self.send(404,b'Not found','text/plain')
ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','10000'))),Handler).serve_forever()
