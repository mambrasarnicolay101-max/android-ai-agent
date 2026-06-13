import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("8.215.23.17", username="root", password="N!colay_No1r.Ai@Agent#Secure")

# Cek apa yang sedang diserver Nginx
cmds = [
    "ls /opt/noir_sovereign/",
    "ls /var/www/html/",
    "cat /etc/nginx/sites-available/default | head -30",
    "ls /opt/noir_sovereign/dist/ 2>/dev/null || echo 'dist folder NOT FOUND'",
    "ls /opt/noir_sovereign/resources/ 2>/dev/null || echo 'resources folder NOT FOUND'"
]

for cmd in cmds:
    print(f"\n[CMD] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"[STDERR] {err}")

ssh.close()
