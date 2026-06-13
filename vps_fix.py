import paramiko
import time

print("[*] Menghubungkan ke VPS Alibaba...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("8.215.23.17", username="root", password="N!colay_No1r.Ai@Agent#Secure")
print("[+] Koneksi SSH berhasil!")

def run(cmd, wait=True):
    print(f"\n[>>] {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    if wait:
        stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out:
        print(f"    {out}")
    if err:
        print(f"    [STDERR] {err}")
    return out

# 1. Pastikan unzip tersedia
run("apt-get install -y unzip")

# 2. Ekstrak ZIP ke /opt/noir_sovereign/
print("\n[*] Mengekstrak file deployment...")
run("cd /opt/noir_sovereign && unzip -o noir_deployment.zip")

# 3. Cek hasil ekstraksi
print("\n[*] Verifikasi struktur folder...")
run("ls -la /opt/noir_sovereign/")
run("ls /opt/noir_sovereign/dist/ 2>/dev/null && echo 'dist OK' || echo 'dist MISSING'")
run("ls /opt/noir_sovereign/resources/ 2>/dev/null && echo 'resources OK' || echo 'resources MISSING'")

# 4. Install Python deps di VPS untuk backend
print("\n[*] Menginstal dependensi Python di VPS...")
run("pip3 install fastapi uvicorn requests paramiko --quiet || pip install fastapi uvicorn requests paramiko --quiet")

# 5. Matikan service lama jika ada, lalu restart Nginx
print("\n[*] Merestart Nginx untuk melayani Dashboard baru...")
run("systemctl restart nginx")
run("systemctl status nginx --no-pager | head -5")

# 6. Jalankan Backend API
print("\n[*] Meluncurkan Backend API di background...")
run("pkill -f backend_api.py 2>/dev/null; sleep 1", wait=True)
run("nohup python3 /opt/noir_sovereign/resources/singularity/backend_api.py > /opt/noir_sovereign/api.log 2>&1 &", wait=False)
time.sleep(2)

# 7. Jalankan Singularity Engine
print("\n[*] Meluncurkan Singularity Autonomous Engine...")
run("pkill -f singularity_orchestrator.py 2>/dev/null; sleep 1", wait=True)
run("nohup python3 /opt/noir_sovereign/resources/singularity/singularity_orchestrator.py --continuous --interval 30 > /opt/noir_sovereign/engine.log 2>&1 &", wait=False)
time.sleep(2)

# 8. Verifikasi proses berjalan
print("\n[*] Verifikasi final proses aktif...")
run("ps aux | grep -E '(backend_api|singularity_orchestrator)' | grep -v grep")
run("curl -s http://localhost:8000/api/state | head -c 100 || echo 'API belum siap'")

print("\n" + "="*60)
print("[SUKSES] Noir Sovereign sepenuhnya aktif di VPS!")
print("[+] Dashboard: http://8.215.23.17")
print("[+] API State: http://8.215.23.17/api/state")
print("="*60)

ssh.close()
