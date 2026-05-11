import paramiko
import os

VPS_IP = '8.215.23.17'
VPS_USER = 'root'
VPS_PASS = 'N!colay_No1r.Ai@Agent#Secure'

def run_build():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
    
    print("--- Cleaning up ---")
    ssh.exec_command('docker stop noir-dashboard noir-brain')
    ssh.exec_command('docker rm noir-dashboard noir-brain')
    
    print("--- Starting Build ---")
    stdin, stdout, stderr = ssh.exec_command('cd /root/noir-agent && docker compose up --build -d')
    
    # We must read from the streams or the command might block if the buffers fill up
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    print("STDOUT:", out)
    print("STDERR:", err)
    
    ssh.close()

if __name__ == "__main__":
    run_build()
