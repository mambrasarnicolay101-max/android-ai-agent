import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS", "N!colay_No1r.Ai@Agent#Secure")
REMOTE_ROOT = "/root/noir-agent"

def force_start_server():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        print("Connected to VPS for Force Restart.")
        
        # Aggressively kill anything on port 80
        commands = [
            "fuser -k 80/tcp",
            "pkill -9 -f gunicorn",
            "pkill -9 -f uvicorn",
            "pkill -9 -f web_server",
            "sleep 2",
            f"cd {REMOTE_ROOT}/noir-ui && nohup python3 -m uvicorn web_server:app --host 0.0.0.0 --port 80 > server.log 2>&1 &"
        ]
        
        for cmd in commands:
            print(f"Exec: {cmd}")
            ssh.exec_command(cmd)
            
        print("Waiting for startup...")
        import time
        time.sleep(5)
        stdin, stdout, stderr = ssh.exec_command("netstat -tuln | grep :80")
        print(f"Status Port 80:\n{stdout.read().decode()}")
        
    finally:
        ssh.close()

if __name__ == "__main__":
    force_start_server()

