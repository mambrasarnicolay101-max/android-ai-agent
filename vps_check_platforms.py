import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("8.215.23.17", username="root", password="N!colay_No1r.Ai@Agent#Secure")

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if out: print(f"    {out[:800]}")
    return out

print("=== PORT & SERVICE STATUS ===")
run("ss -tlnp | awk '{print $1, $4, $7}'")

print("\n=== DOCKER / DVWA CHECK ===")
run("docker ps 2>/dev/null || echo 'Docker tidak tersedia'")
run("ls /opt/dvwa/ 2>/dev/null || echo 'DVWA tidak terinstall'")
run("ls /var/www/html/ 2>/dev/null")

print("\n=== RUNNING WEB SERVERS ===")
run("ps aux | grep -E '(apache|nginx|python|php|node)' | grep -v grep")

print("\n=== DVWA_ATTACKER SCRIPT CONTENT ===")
run("head -30 /opt/noir_sovereign/resources/dvwa_attacker.py 2>/dev/null || echo 'File tidak ditemukan di VPS'")

print("\n=== VPS HTB BRIDGE ===")
run("head -30 /opt/noir_sovereign/resources/vps_htb_bridge.py 2>/dev/null || echo 'File tidak ditemukan'")

ssh.close()
