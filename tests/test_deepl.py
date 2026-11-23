import io
import json
import unittest
from unittest.mock import patch
import server

class DeepLTests(unittest.TestCase):
    def test_request_routing_and_mapping(self):
        for plan, key, host in [('auto','fake:fx','api-free.deepl.com'),('auto','fake','api.deepl.com'),('pro','fake:fx','api.deepl.com')]:
            with patch('urllib.request.urlopen', return_value=io.BytesIO(b'{"translations":[{"text":"Hallo"}]}')) as call:
                self.assertEqual(server.translate_deepl({'key':key,'text':'Hello\n\nWorld','lang':'zh','plan':plan}), 'Hallo')
                request=call.call_args[0][0]
                self.assertEqual(request.host,host)
                body=json.loads(request.data)
                self.assertEqual(body['target_lang'],'ZH-HANS')
                self.assertEqual(body['source_lang'],'EN')
                self.assertTrue(body['preserve_formatting'])
                self.assertEqual(request.get_header('Authorization'),'DeepL-Auth-Key '+key)
    def test_invalid_input(self):
        for data in [{},{'key':'x','text':'Hello','lang':'xyz'}, {'key':'x\nsecret','text':'Hello','lang':'de'}]:
            with self.assertRaises(ValueError):server.translate_deepl(data)
    def test_invalid_response(self):
        with patch('urllib.request.urlopen', return_value=io.BytesIO(b'{"translations":[]}')):
            with self.assertRaises(IndexError):server.translate_deepl({'key':'fake','text':'Hello','lang':'de'})

if __name__=='__main__':unittest.main()
