import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("8.215.23.17", username="root", password="N!colay_No1r.Ai@Agent#Secure")
print("[+] Koneksi SSH berhasil!")

def run(cmd, wait=True):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    if wait: stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out: print(f"    {out[:600]}")
    if err and 'warning' not in err.lower(): print(f"    [ERR] {err[:300]}")
    return out

# 1. Cek firewall internal VPS
print("\n[*] Cek status firewall internal...")
run("ufw status 2>/dev/null || echo 'ufw tidak aktif'")
run("iptables -L INPUT --line-numbers -n 2>/dev/null | head -15")

# 2. Coba buka port 9090 via iptables
print("\n[*] Membuka port 9090 via iptables...")
run("iptables -I INPUT -p tcp --dport 9090 -j ACCEPT 2>/dev/null || true")
run("ufw allow 9090/tcp 2>/dev/null || true")

# 3. Verifikasi Docker DVWA masih berjalan
print("\n[*] Verifikasi Docker DVWA...")
run("docker ps | grep dvwa")
run("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/")

# 4. Buat Nginx proxy /dvwa/ → localhost:9090 sebagai solusi cadangan
print("\n[*] Mengkonfigurasi Nginx proxy untuk DVWA di /dvwa/...")

nginx_conf = (
    "server {\n"
    "    listen 80;\n"
    "    server_name _;\n"
    "    root /opt/noir_sovereign/dist;\n"
    "    index index.html;\n\n"
    "    location / {\n"
    "        try_files $uri $uri/ /index.html;\n"
    "    }\n\n"
    "    location /api/ {\n"
    "        proxy_pass http://127.0.0.1:8000;\n"
    "        proxy_set_header Host $host;\n"
    "        proxy_set_header X-Real-IP $remote_addr;\n"
    "    }\n\n"
    "    # DVWA Proxy - accessible di /dvwa/\n"
    "    location /dvwa/ {\n"
    "        proxy_pass http://127.0.0.1:9090/;\n"
    "        proxy_set_header Host $host;\n"
    "        proxy_set_header X-Real-IP $remote_addr;\n"
    "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
    "        proxy_set_header X-Forwarded-Proto $scheme;\n"
    "        proxy_redirect http://127.0.0.1:9090/ /dvwa/;\n"
    "        proxy_cookie_path / /dvwa/;\n"
    "    }\n"
    "}\n"
)

sftp = ssh.open_sftp()
with sftp.open('/etc/nginx/sites-available/default', 'w') as f:
    f.write(nginx_conf)
sftp.close()

run("nginx -t 2>&1")
run("systemctl reload nginx 2>/dev/null || systemctl restart nginx")

# 5. Verifikasi semua endpoint
print("\n[*] Verifikasi semua endpoint setelah konfigurasi...")
h_dash = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
h_api  = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/api/state")
h_dvwa = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/dvwa/")
h_dvwa_direct = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/")

print("\n" + "="*65)
print("AKSES PUBLIK - SEMUA MELALUI PORT 80 (FIREWALL SAFE)")
print(f"  Dashboard Noir : http://8.215.23.17/          [{h_dash}]")
print(f"  API Live State : http://8.215.23.17/api/state [{h_api}]")
print(f"  DVWA via Proxy : http://8.215.23.17/dvwa/     [{h_dvwa}]")
print(f"  DVWA Direct    : http://8.215.23.17:9090      [{h_dvwa_direct}] (mungkin diblokir firewall cloud)")
print("="*65)
print("\n[TIP] Jika port 9090 masih timeout, buka Alibaba Cloud Console →")
print("      Security Groups → tambah rule: TCP port 9090 0.0.0.0/0")

ssh.close()
