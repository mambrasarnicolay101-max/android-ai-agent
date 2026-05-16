import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS", "N!colay_No1r.Ai@Agent#Secure")
REMOTE_ROOT = "/root/noir-agent"

def debug_vps():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        print("Connected to VPS for Debugging.")
        
        cmds = [
            # 1. Cek apakah uvicorn sedang berjalan
            "ps aux | grep uvicorn",
            # 2. Cek port yang sedang mendengarkan (listening)
            "netstat -tuln | grep 8765",
            # 3. Baca log server terakhir
            f"tail -n 50 {REMOTE_ROOT}/noir-ui/server.log",
            # 4. Cek firewall lokal (ufw/iptables)
            "ufw status || iptables -L -n | grep 8765"
        ]
        
        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
    finally:
        ssh.close()

if __name__ == "__main__":
    debug_vps()

