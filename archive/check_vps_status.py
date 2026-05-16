import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS", "N!colay_No1r.Ai@Agent#Secure")

def check_vps():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        print("Connected.")
        
        cmds = [
            "ls -F /root",
            "ls -F /root/android-ai-agent",
            "ps aux | grep uvicorn"
        ]
        
        for cmd in cmds:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
    finally:
        ssh.close()

if __name__ == "__main__":
    check_vps()

