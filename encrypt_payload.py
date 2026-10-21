import base64
import hashlib
import json
import os
import ssl
import urllib.request
import urllib.parse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENCRYPTION_KEY = "bLs6z8iv3gWpsvyeabFosDjb4YQe7jdU13rI"

def encrypt_payload(payload_dict):
    key = hashlib.sha256(ENCRYPTION_KEY.encode('utf-8')).digest()
    iv = os.urandom(12)
    data = json.dumps(payload_dict).encode('utf-8')
    
    aesgcm = AESGCM(key)
    # aesgcm.encrypt returns ciphertext + 16-byte tag
    ct_and_tag = aesgcm.encrypt(iv, data, None)
    
    combined = iv + ct_and_tag
    return base64.b64encode(combined).decode('utf-8')

def decrypt_payload(b64_str):
    key = hashlib.sha256(ENCRYPTION_KEY.encode('utf-8')).digest()
    combined = base64.b64decode(b64_str)
    iv = combined[:12]
    ct_and_tag = combined[12:]
    aesgcm = AESGCM(key)
    data = aesgcm.decrypt(iv, ct_and_tag, None)
    return json.loads(data.decode('utf-8'))

# Test encrypt/decrypt locally
test_p = {"transcription": "hello test", "summary": "hello test"}
enc = encrypt_payload(test_p)
dec = decrypt_payload(enc)
print("Encrypted:", enc)
print("Decrypted:", dec)
