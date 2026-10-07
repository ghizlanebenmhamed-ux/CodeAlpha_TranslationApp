import json,threading,unittest,urllib.request,urllib.error
from unittest.mock import patch,MagicMock
from http.server import ThreadingHTTPServer
import server

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        threading.Thread(target=cls.http.serve_forever,daemon=True).start();cls.url=f'http://127.0.0.1:{cls.http.server_port}'
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close()
    def request(self,payload):
        req=urllib.request.Request(self.url+'/api/translate',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as r:return r.code,json.load(r)
    def test_languages(self):
        with urllib.request.urlopen(self.url+'/api/languages') as r:self.assertGreaterEqual(len(json.load(r)),20)
    def test_home(self):
        with urllib.request.urlopen(self.url) as r:self.assertIn('Translation App',r.read().decode())
    def test_blank(self):self.assertEqual(self.request(dict(text='',source='en',target='fr'))[0],400)
    def test_invalid_language(self):self.assertEqual(self.request(dict(text='hi',source='bad',target='fr'))[0],400)
    def test_byte_limit(self):self.assertEqual(self.request(dict(text='中'*167,source='zh-CN',target='en'))[0],400)
    def test_same_language(self):self.assertEqual(self.request(dict(text='Hello',source='en',target='en'))[1]['translation'],'Hello')
    def test_success_response(self):
        with patch('server.translate',return_value='Bonjour'):
            code,data=self.request(dict(text='Hello',source='en',target='fr'));self.assertEqual(code,200);self.assertEqual(data['translation'],'Bonjour')
    def test_network_error(self):
        with patch('server.translate',side_effect=urllib.error.URLError('offline')):self.assertEqual(self.request(dict(text='hi',source='en',target='fr'))[0],502)
    def test_quota_error(self):
        with patch('server.translate',side_effect=ValueError('quota reached')):self.assertIn('quota',self.request(dict(text='hi',source='en',target='fr'))[1]['error'])
    def test_api_decoding(self):
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps({'responseStatus':200,'responseData':{'translatedText':'A &amp; B'}}).encode()
        server.translate.cache_clear()
        with patch('server.urllib.request.urlopen',return_value=response):self.assertEqual(server.translate('Unique testing sentence','en','fr'),'A & B')
if __name__=='__main__':unittest.main(verbosity=2)
