"""Loopback-only static editor and a narrowly scoped DeepL bridge."""
import json
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOSTS = {'127.0.0.1:8765', 'localhost:8765'}
ORIGINS = {'http://127.0.0.1:8765', 'http://localhost:8765'}
TARGETS = {'es': 'ES', 'pt': 'PT-BR', 'de': 'DE', 'fr': 'FR', 'it': 'IT',
           'ja': 'JA', 'ko': 'KO', 'zh': 'ZH-HANS', 'ar': 'AR', 'id': 'ID', 'th': 'TH', 'vi': 'VI',
           'hu': 'HU', 'pl': 'PL', 'cs': 'CS', 'bg': 'BG', 'ro': 'RO', 'ru': 'RU',
           'he': 'HE', 'hr': 'HR', 'lt': 'LT'}


def translate_deepl(data):
    key = data.get('key', '')
    text = data.get('text', '')
    plan = data.get('plan', 'auto')
    if not isinstance(key, str) or not key.strip() or len(key) > 1000 or '\n' in key or '\r' in key:
        raise ValueError('DeepL API Key 无效')
    if not isinstance(text, str) or not text.strip() or len(text.encode('utf-8')) > 100000:
        raise ValueError('文案为空或超过 DeepL 单次请求限制')
    if data.get('lang') not in TARGETS or plan not in {'auto', 'free', 'pro'}:
        raise ValueError('语言或 API 类型无效')
    free = plan == 'free' or (plan == 'auto' and key.strip().endswith(':fx'))
    url = 'https://api-free.deepl.com/v2/translate' if free else 'https://api.deepl.com/v2/translate'
    payload = json.dumps({'text': [text], 'source_lang': 'EN', 'target_lang': TARGETS[data['lang']],
                          'preserve_formatting': True}, ensure_ascii=False).encode('utf-8')
    request = urllib.request.Request(url, data=payload, headers={
        'Authorization': 'DeepL-Auth-Key ' + key.strip(), 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read(1024 * 1024))
    translated = result.get('translations', [{}])[0].get('text')
    if not isinstance(translated, str) or not translated.strip():
        raise ValueError('DeepL 未返回有效译文')
    return translated.strip()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'dist'), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def json_response(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.headers.get('Host') not in HOSTS:
            return self.json_response(403, {'error': '仅允许本机访问'})
        if self.path == '/api/health':
            return self.json_response(200, {'service': 'hn-ad-studio', 'version': 2, 'deepl': True})
        super().do_GET()

    def do_POST(self):
        if self.headers.get('Host') not in HOSTS or self.headers.get('Origin') not in ORIGINS:
            return self.json_response(403, {'error': '仅接受工作台同源请求'})
        if self.path != '/api/deepl':
            return self.json_response(404, {'error': '接口不存在'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 700000 or self.headers.get_content_type() != 'application/json':
                return self.json_response(400, {'error': '请求格式或大小无效'})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('请求格式无效')
            return self.json_response(200, {'text': translate_deepl(data)})
        except urllib.error.HTTPError as error:
            messages = {400: '语言或参数不受支持', 403: '密钥无效或 API 类型不匹配',
                        429: '请求频率受限', 456: '配额已用尽'}
            return self.json_response(502, {'error': 'DeepL：' + messages.get(error.code, '服务暂不可用'),
                                            'upstreamStatus': error.code})
        except (ValueError, TypeError, KeyError, IndexError):
            return self.json_response(400, {'error': 'DeepL 请求或响应格式无效'})
        except (OSError, urllib.error.URLError):
            return self.json_response(502, {'error': 'DeepL 连接失败或超时'})


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
