import html
import json
import threading
import urllib.parse
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import lru_cache

ROOT=Path(__file__).parent
LANGUAGES={'en':'English','fr':'French','ar':'Arabic','zh-CN':'Chinese (Simplified)','es':'Spanish','de':'German','it':'Italian','pt':'Portuguese','ja':'Japanese','ko':'Korean','ru':'Russian','hi':'Hindi','tr':'Turkish','nl':'Dutch','pl':'Polish','sv':'Swedish','el':'Greek','id':'Indonesian','vi':'Vietnamese','th':'Thai','uk':'Ukrainian','ro':'Romanian','cs':'Czech','da':'Danish'}

@lru_cache(maxsize=128)
def translate(text,source,target):
    if source==target:return text
    params=urllib.parse.urlencode({'q':text,'langpair':source+'|'+target})
    request=urllib.request.Request('https://api.mymemory.translated.net/get?'+params,headers={'User-Agent':'TranslationApp/1.0'})
    with urllib.request.urlopen(request,timeout=25) as response:data=json.load(response)
    if str(data.get('responseStatus'))!='200' or data.get('quotaFinished'):
        raise ValueError(data.get('responseDetails') or 'Translation quota reached. Please try again later.')
    result=data.get('responseData',{}).get('translatedText')
    if not isinstance(result,str) or not result.strip():raise ValueError('The translation service returned no text.')
    return html.unescape(result)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'public'),**kwargs)
    def send_json(self,status,payload):
        encoded=json.dumps(payload,ensure_ascii=False).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(encoded)));self.end_headers();self.wfile.write(encoded)
    def do_GET(self):
        if self.path=='/api/languages':return self.send_json(200,LANGUAGES)
        return super().do_GET()
    def do_POST(self):
        if self.path!='/api/translate':return self.send_json(404,{'error':'Endpoint not found.'})
        try:
            length=int(self.headers.get('Content-Length',0))
            if length<=0 or length>10000:raise ValueError('Invalid request size.')
            payload=json.loads(self.rfile.read(length));text=payload.get('text','');source=payload.get('source');target=payload.get('target')
            if not isinstance(text,str) or not text.strip():raise ValueError('Enter some text first.')
            if source not in LANGUAGES or target not in LANGUAGES:raise ValueError('Choose valid source and target languages.')
            if len(text.encode('utf-8'))>500:raise ValueError('Text exceeds 500 UTF-8 bytes. Shorten it and try again.')
            return self.send_json(200,{'translation':translate(text,source,target),'provider':'MyMemory'})
        except (ValueError,TypeError,AttributeError) as error:return self.send_json(400,{'error':str(error)})
        except (urllib.error.URLError,TimeoutError):return self.send_json(502,{'error':'Cannot reach the translation service. Check your internet connection and try again.'})
        except Exception:return self.send_json(502,{'error':'The translation service could not process this request. Try again later.'})

def main():
    server=None
    for port in range(8765,8785):
        try:server=ThreadingHTTPServer(('127.0.0.1',port),Handler);break
        except OSError:continue
    if server is None:raise RuntimeError('No available local port. Close previous copies and retry.')
    url=f'http://127.0.0.1:{server.server_port}'
    print('Translation App:',url,flush=True)
    print('Keep this terminal open. Press Ctrl+C to stop.',flush=True)
    threading.Timer(1,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
