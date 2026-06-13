import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

VPS_IP   = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS", "N!colay_No1r.Ai@Agent#Secure")

def run_diag():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        print("Connected successfully to VPS.")
        
        commands = [
            ("Docker Containers", "docker ps -a"),
            ("Systemd Services Active Status", "systemctl is-active noir-sovereign.service noir-orchestrator.service || true"),
            ("Systemd Services Status details", "systemctl status noir-sovereign.service --no-pager || true"),
            ("Port 80 process listener", "netstat -tulnp | grep :80 || ss -tulnp | grep :80 || true"),
            ("HTML files version search on VPS", "grep -in 'v29' /root/noir-agent/noir-ui/*.html || true"),
            ("HTML files v30 search on VPS", "grep -in 'v30' /root/noir-agent/noir-ui/*.html || true"),
            ("Check index.html path on VPS", "ls -l /root/noir-agent/noir-ui/index.html || true"),
            ("Recent logs from server.log", "tail -n 20 /root/noir-agent/noir-ui/server.log || true"),
            ("Processes matching python", "ps aux | grep python || true")
        ]
        
        for title, cmd in commands:
            print(f"\n=== {title} ===")
            print(f"Running: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode('utf-8', errors='replace').strip()
            err = stderr.read().decode('utf-8', errors='replace').strip()
            if out:
                print(out)
            if err:
                print("Error:", err)
    except Exception as e:
        print("Error connecting:", e)
    finally:
        ssh.close()

if __name__ == "__main__":
    run_diag()
