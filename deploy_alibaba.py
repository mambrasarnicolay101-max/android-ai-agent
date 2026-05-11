import paramiko
import os
import tarfile
from scp import SCPClient
import sys

# Configuration from .env would be better, but we'll use the known working values from restart_vps.py
VPS_IP = '8.215.23.17'
VPS_USER = 'root'
VPS_PASS = 'N!colay_No1r.Ai@Agent#Secure'
REMOTE_PATH = '/root/noir-agent'

def create_bundle():
    print("[*] Creating deployment bundle...")
    bundle_name = 'deploy_bundle.tar.gz'
    with tarfile.open(bundle_name, "w:gz") as tar:
        for item in ['noir-ui', 'noir-vps', 'sovereign_boot.py', 'purge_system.py', 'pc_launcher.py', 'docker-compose.yml', 'Dockerfile']:
            if os.path.exists(item):
                tar.add(item)
        if os.path.exists('.env.vps'):
            tar.add('.env.vps', arcname='.env')
    return bundle_name

def deploy():
    bundle = create_bundle()
    
    try:
        print(f"[*] Connecting to Alibaba VPS ({VPS_IP})...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        
        print("[*] Uploading bundle...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(bundle, f'/tmp/{bundle}')
            
        print("[*] Extracting bundle on VPS...")
        ssh.exec_command(f'rm -rf /root/android-ai-agent') # Clean up accidental path
        ssh.exec_command(f'mkdir -p {REMOTE_PATH}')
        ssh.exec_command(f'tar -xzf /tmp/{bundle} -C {REMOTE_PATH}')
        
        print("[*] Rebuilding Sovereign Services (Docker)...")
        # Aggressive restart: stop, remove, and rebuild using Docker Compose V2
        ssh.exec_command('docker stop noir-dashboard noir-brain')
        ssh.exec_command('docker rm noir-dashboard noir-brain')
        stdin, stdout, stderr = ssh.exec_command(f'cd {REMOTE_PATH} && docker compose up --build -d')
        out_str = stdout.read().decode('utf-8', 'replace')
        print(out_str.encode('ascii', 'ignore').decode('ascii'))
        
        print("[*] Verifying container status...")
        stdin, stdout, stderr = ssh.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"')
        ps_str = stdout.read().decode('utf-8', 'replace')
        print(ps_str.encode('ascii', 'ignore').decode('ascii'))
        
        ssh.close()
        print(f"\n[SUCCESS] Deployment V21.2 ELITE AEGIS completed on {VPS_IP}")
        
    except Exception as e:
        print(f"[ERROR] Deployment failed: {e}")
    finally:
        if os.path.exists(bundle):
            os.remove(bundle)

if __name__ == "__main__":
    deploy()
