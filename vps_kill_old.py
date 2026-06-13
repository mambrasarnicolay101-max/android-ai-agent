import paramiko
import sys
import time

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
    if out: print(f"    {out[:600]}")
    if err: print(f"    [ERR] {err[:300]}")
    return out

# 1. Identifikasi dan bunuh proses Python lama yang menguasai port 80 dan 8080
print("\n[*] Membunuh proses Python lama (Dashboard V30.1) di port 80 & 8080...")
run("ss -tlnp | grep -E ':(80|8080)'")
run("fuser -k 80/tcp 2>&1 || true")
run("fuser -k 8080/tcp 2>&1 || true")
run("kill -9 1595575 2>/dev/null || true")
run("kill -9 1595577 2>/dev/null || true")
run("sleep 2")

# 2. Verifikasi port 80 sudah bebas
print("\n[*] Memverifikasi port 80 sudah bebas...")
result = run("ss -tlnp | grep ':80' || echo 'Port 80 BEBAS!'")

# 3. Start Nginx sekarang
print("\n[*] Menyalakan Nginx untuk serve Dashboard React baru...")
run("systemctl start nginx")
run("systemctl is-active nginx")
run("systemctl enable nginx")

# 4. Pastikan Singularity Engine juga berjalan
print("\n[*] Memastikan Singularity Engine aktif...")
run("pkill -f singularity_orchestrator.py 2>/dev/null; sleep 1")
run("nohup python3 /opt/noir_sovereign/resources/singularity/singularity_orchestrator.py --continuous --interval 30 > /opt/noir_sovereign/engine.log 2>&1 &")
time.sleep(2)

# 5. Verifikasi semua sistem online
print("\n[*] Verifikasi final semua sistem...")
run("ps aux | grep -E '(backend_api|singularity_orchestrator|nginx)' | grep -v grep")

http_code = run("curl -s -o /dev/null -w '%{http_code}' http://localhost/")
api_result = run("curl -s http://localhost:8000/api/state")

print("\n" + "="*60)
if "200" in http_code:
    print("[SUKSES TOTAL] Noir Sovereign Dashboard ONLINE!")
    print(f"[+] Dashboard HTTP Status: {http_code}")
else:
    print(f"[!] Dashboard HTTP Status: {http_code}")
print("[+] Akses dari browser: http://8.215.23.17")
print("[+] API State: http://8.215.23.17/api/state")
print("="*60)

ssh.close()
