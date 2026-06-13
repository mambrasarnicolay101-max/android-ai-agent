import paramiko
import sys

# Force UTF-8 output untuk menghindari cp1252 UnicodeError di Windows
sys.stdout.reconfigure(encoding='utf-8')

print("[*] Menghubungkan ke VPS Alibaba...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("8.215.23.17", username="root", password="N!colay_No1r.Ai@Agent#Secure")
print("[+] Koneksi berhasil!")

def run(cmd, wait=True):
    print(f"\n[>>] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    if wait:
        stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out: print(f"    {out[:800]}")
    if err: print(f"    [ERR] {err[:400]}")
    return out

# 1. Nginx sudah test OK — cek kenapa restart gagal
print("\n[*] Cek konflik port 80...")
run("ss -tlnp | grep ':80'")
run("fuser 80/tcp 2>&1 || echo 'port check done'")

# 2. Coba stop paksa semua yang pakai port 80, lalu start ulang nginx
run("nginx -s stop 2>/dev/null || true")
run("pkill nginx 2>/dev/null || true")
run("sleep 2")
run("systemctl start nginx 2>&1 || nginx 2>&1")
run("systemctl status nginx --no-pager 2>&1 | head -8")

# 3. Tulis ulang konfigurasi Nginx via SFTP (lebih aman dari echo/heredoc)
print("\n[*] Menulis ulang konfigurasi Nginx via SFTP...")
nginx_conf = (
    "server {\n"
    "    listen 80;\n"
    "    server_name _;\n"
    "    root /opt/noir_sovereign/dist;\n"
    "    index index.html;\n"
    "    location / {\n"
    "        try_files $uri $uri/ /index.html;\n"
    "    }\n"
    "    location /api/ {\n"
    "        proxy_pass http://127.0.0.1:8000;\n"
    "        proxy_set_header Host $host;\n"
    "        proxy_set_header X-Real-IP $remote_addr;\n"
    "    }\n"
    "}\n"
)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-available/default', 'w') as f:
    f.write(nginx_conf)
sftp.close()
print("    [+] Config ditulis via SFTP")

run("rm -f /etc/nginx/sites-enabled/default")
run("ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default")
run("nginx -t 2>&1")
run("systemctl restart nginx 2>&1 || nginx 2>&1")
run("systemctl is-active nginx 2>&1")

# 4. Verifikasi akhir
print("\n[*] Verifikasi Dashboard online...")
result = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
if "200" in result:
    print("\n    *** DASHBOARD ONLINE — HTTP 200 OK ***")
else:
    print(f"\n    [!] HTTP Status: {result}")
    run("curl -v http://localhost/ 2>&1 | head -30")

# 5. Pastikan proses AI engine berjalan
print("\n[*] Status proses AI Engine...")
run("ps aux | grep -E '(backend_api|singularity_orchestrator)' | grep -v grep")
run("curl -s http://localhost:8000/api/state")

print("\n" + "="*60)
print("HASIL AKHIR")
print("[+] Dashboard: http://8.215.23.17")
print("[+] API:       http://8.215.23.17/api/state")
print("="*60)

ssh.close()
