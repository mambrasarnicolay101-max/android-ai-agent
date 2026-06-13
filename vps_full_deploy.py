import paramiko
import zipfile
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

HOST = "8.215.23.17"
USER = "root"
PASS = "N!colay_No1r.Ai@Agent#Secure"

print("[*] Menghubungkan ke VPS Alibaba...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)
print("[+] Koneksi SSH berhasil!\n")

def run(cmd, wait=True, show=True):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    if wait:
        stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if show:
        if out: print(f"    {out[:600]}")
    return out

# ========================================================
# TAHAP 1: Upload dist baru (dengan URL API yang sudah diperbaiki)
# ========================================================
print("=" * 60)
print("TAHAP 1: Upload Dashboard React Terbaru ke VPS")
print("=" * 60)

dist_path = r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\noir_dashboard\dist"
zip_path = r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\dist_only.zip"

print("[*] Mengemas folder dist...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(dist_path):
        for file in files:
            fp = os.path.join(root, file)
            arcname = os.path.relpath(fp, dist_path)
            zf.write(fp, arcname=os.path.join("dist", arcname))
print(f"[+] ZIP dibuat: {zip_path}")

print("[*] Mengunggah dist ke VPS...")
from scp import SCPClient
with SCPClient(ssh.get_transport()) as scp:
    scp.put(zip_path, remote_path='/tmp/dist_only.zip')
    scp.put(r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\vps_inject_proof.py",
            remote_path='/tmp/vps_inject_proof.py')
print("[+] Upload selesai!")

run("rm -rf /opt/noir_sovereign/dist && cd /tmp && unzip -o dist_only.zip -d /opt/noir_sovereign/")
print("[+] Dashboard React terbaru berhasil di-deploy!")

# ========================================================
# TAHAP 2: Jalankan Skrip Bukti Evolusi di VPS
# ========================================================
print("\n" + "=" * 60)
print("TAHAP 2: Menjalankan Siklus Evolusi Otonom Noir di VPS")
print("=" * 60)

print("[*] Menjalankan proof-of-evolution script...")
stdin, stdout, stderr = ssh.exec_command("python3 /tmp/vps_inject_proof.py")
stdout.channel.recv_exit_status()
output = stdout.read().decode('utf-8', errors='replace')
print(output)

# ========================================================
# TAHAP 3: Restart API dan verifikasi state.json berisi data
# ========================================================
print("\n" + "=" * 60)
print("TAHAP 3: Verifikasi State & Restart Services")
print("=" * 60)

run("pkill -f backend_api.py 2>/dev/null; sleep 1")
run("nohup python3 /opt/noir_sovereign/resources/singularity/backend_api.py > /opt/noir_sovereign/api.log 2>&1 &")
time.sleep(2)

print("\n[*] Verifikasi API mengembalikan data nyata...")
api_result = run("curl -s http://localhost:8000/api/state")
print(f"\n[API RESPONSE SAMPLE]:\n{api_result[:400]}")

run("systemctl reload nginx 2>/dev/null || systemctl restart nginx 2>/dev/null || true")

print("\n[*] Verifikasi Dashboard merespons...")
http_code = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/")

print("\n" + "=" * 60)
if "200" in http_code:
    print("[SUKSES TOTAL] Semua sistem operasional!")
print("[+] Dashboard Noir: http://8.215.23.17")
print("[+] API State Live: http://8.215.23.17/api/state")
print("[+] Log Aktivitas Mesin: /opt/noir_sovereign/engine.log")
print("=" * 60)

ssh.close()
