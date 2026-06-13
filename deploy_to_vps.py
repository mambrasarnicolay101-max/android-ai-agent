import os
import zipfile
import paramiko
from scp import SCPClient

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            # relative path to preserve directory structure inside zip
            rel_path = os.path.relpath(file_path, os.path.dirname(path))
            ziph.write(file_path, arcname=rel_path)

def create_archive():
    print("[*] Mengemas Dashboard dan Mesin Noir Sovereign...")
    zip_path = "noir_deployment.zip"
    dashboard_path = r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\noir_dashboard\dist"
    ai_engine_path = r"C:\Users\ASUS\.gemini\config\plugins\noir-sovereign\skills\autonomous-penetration\resources"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(dashboard_path):
            zipdir(dashboard_path, zipf)
        if os.path.exists(ai_engine_path):
            zipdir(ai_engine_path, zipf)
            
    print(f"[+] Berhasil membuat {zip_path}")
    return zip_path

def deploy_to_vps(zip_file, host, user, password):
    print(f"[*] Menghubungkan ke VPS {host}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        
        # 1. Setup Direktori di VPS
        print("[*] Menyiapkan direktori di VPS (/opt/noir_sovereign)...")
        ssh.exec_command("rm -rf /opt/noir_sovereign")
        ssh.exec_command("mkdir -p /opt/noir_sovereign")
        
        # 2. Upload file
        print("[*] Mengunggah file instalasi...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(zip_file, remote_path='/opt/noir_sovereign/')
            
        # 3. Ekstrak dan Install Dependensi
        print("[*] Mengekstrak dan mengatur environment (Python, Nginx)...")
        commands = [
            "cd /opt/noir_sovereign",
            "apt-get update && apt-get install -y unzip nginx python3-pip",
            "unzip -o noir_deployment.zip",
            "pip3 install fastapi uvicorn requests paramiko"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.channel.recv_exit_status() # wait for command to finish
            
        # 4. Setup Nginx untuk Dashboard React
        nginx_conf = """
server {
    listen 80;
    server_name _;
    
    root /opt/noir_sovereign/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
        """
        ssh.exec_command(f"echo '{nginx_conf}' > /etc/nginx/sites-available/default")
        ssh.exec_command("systemctl restart nginx")
        
        # 5. Setup Systemd Service untuk Mesin Singularity
        service_conf = """
[Unit]
Description=Noir Sovereign Singularity Engine
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/noir_sovereign/resources/singularity
ExecStart=/usr/bin/python3 singularity_orchestrator.py --continuous --interval 30
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
        """
        
        api_service_conf = """
[Unit]
Description=Noir Sovereign Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/noir_sovereign/resources/singularity
ExecStart=/usr/local/bin/uvicorn backend_api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
        """
        
        ssh.exec_command(f"echo '{service_conf}' > /etc/systemd/system/noir-engine.service")
        ssh.exec_command(f"echo '{api_service_conf}' > /etc/systemd/system/noir-api.service")
        
        ssh.exec_command("systemctl daemon-reload")
        ssh.exec_command("systemctl enable noir-api.service")
        ssh.exec_command("systemctl start noir-api.service")
        ssh.exec_command("systemctl enable noir-engine.service")
        ssh.exec_command("systemctl start noir-engine.service")
        
        print(f"[+] DEPLOYMENT SUKSES! Noir Sovereign kini hidup di {host}")
        print(f"[+] Akses Dashboard dari mana saja: http://{host}")
        
    except Exception as e:
        print(f"[-] Error deployment: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    zip_path = create_archive()
    deploy_to_vps(zip_path, "8.215.23.17", "root", "N!colay_No1r.Ai@Agent#Secure")
