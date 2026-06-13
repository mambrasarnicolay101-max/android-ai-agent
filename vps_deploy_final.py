import paramiko
import zipfile
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("8.215.23.17", username="root", password="N!colay_No1r.Ai@Agent#Secure")

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if out: print(f"    {out[:400]}")
    return out

# Package new dist
dist_path = r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\noir_dashboard\dist"
zip_path = r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\dist_only.zip"

print("[*] Mengemas dist terbaru (dengan PlatformPanel)...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(dist_path):
        for file in files:
            fp = os.path.join(root, file)
            arcname = os.path.relpath(fp, dist_path)
            zf.write(fp, arcname=os.path.join("dist", arcname))
print("[+] ZIP siap!")

# Upload & extract
print("[*] Mengunggah ke VPS...")
from scp import SCPClient
with SCPClient(ssh.get_transport()) as scp:
    scp.put(zip_path, remote_path='/tmp/dist_only.zip')

print("[*] Mengganti dist lama dengan yang baru...")
run("rm -rf /opt/noir_sovereign/dist")
run("cd /tmp && unzip -o dist_only.zip -d /opt/noir_sovereign/")
run("ls /opt/noir_sovereign/dist/")

# Pastikan DVWA port 9090 bisa diakses dari luar (expose via Nginx)
print("\n[*] Membuka akses DVWA port 9090 untuk verifikasi publik...")
run("docker inspect dvwa_target 2>/dev/null | grep -E '(Status|Port)' | head -5")

# Update Nginx config untuk tambahkan proxy ke DVWA juga
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

run("nginx -t 2>&1")
run("systemctl reload nginx 2>/dev/null || systemctl restart nginx")

# Verifikasi akhir
print("\n[*] Verifikasi semua endpoint...")
http_dash = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
http_api  = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/api/state")
http_dvwa = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/ 2>/dev/null")

print("\n" + "="*60)
print("STATUS AKHIR SEMUA LAYANAN")
print(f"  Dashboard Noir : http://8.215.23.17       [{http_dash}]")
print(f"  API State      : http://8.215.23.17/api/state [{http_api}]")
print(f"  DVWA Platform  : http://8.215.23.17:9090  [{http_dvwa}]")
print("="*60)

ssh.close()
