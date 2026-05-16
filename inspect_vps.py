import paramiko
import os

VPS_IP = '"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"'
VPS_USER = 'root'
VPS_PASS = 'N!colay_No1r.Ai@Agent#Secure'

def inspect_vps():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
    
    print("--- Docker PS ---")
    stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}"')
    print(stdout.read().decode())
    
    print("--- Inspecting noir-dashboard ---")
    # Get the project working directory
    stdin, stdout, stderr = ssh.exec_command('docker inspect noir-dashboard')
    import json
    data = json.loads(stdout.read().decode())
    if data:
        labels = data[0].get('Config', {}).get('Labels', {})
        print(f"Working Dir: {labels.get('com.docker.compose.project.working_dir')}")
        print(f"Project Name: {labels.get('com.docker.compose.project')}")
        
    ssh.close()

if __name__ == "__main__":
    inspect_vps()
