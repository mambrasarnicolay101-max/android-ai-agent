import paramiko
import os

VPS_IP = '"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"'
VPS_USER = 'root'
VPS_PASS = 'N!colay_No1r.Ai@Agent#Secure'

def run_debug():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
    
    print("--- Running Docker-Compose ---")
    stdin, stdout, stderr = ssh.exec_command('cd /root/noir-agent && docker-compose up --build -d')
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())
    
    print("--- Docker PS ---")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a')
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    run_debug()
