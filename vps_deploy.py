import paramiko
import os

hostname = "os.environ.get("NOIR_VPS_IP", "8.215.23.17")
username = "root"
password = "N!colay_No1r.Ai@Agent#Secure"
vps_root = "/opt/noir-dashboard"

def execute_cmd(ssh, cmd):
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(f"OUT: {out}")
    if err: print(f"ERR: {err}")
    return out

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    
    print(f"Target VPS Root: {vps_root}")
    
    # 2. Upload files
    sftp = ssh.open_sftp()
    
    files_to_sync = [
        ("noir-ui/index.html", f"{vps_root}/index.html"),  # Map noir-ui/index.html to root index.html on VPS
        ("noir-vps/ai_router.py", f"{vps_root}/ai_router.py"),
        ("knowledge/api_pool.json", f"{vps_root}/api_pool.json")
    ]
    
    local_base = "c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent"
    
    for local_rel, vps_abs in files_to_sync:
        local_abs = os.path.join(local_base, local_rel)
        if os.path.exists(local_abs):
            print(f"Uploading {local_rel} -> {vps_abs}")
            sftp.put(local_abs, vps_abs)
        else:
            print(f"Skip: {local_abs} not found locally.")
            
    sftp.close()
    
    # 3. Restart services on VPS
    print("--- Restarting services on VPS ---")
    # Kill any process running server.py
    execute_cmd(ssh, "pkill -f server.py || true")
    
    # Start server.py on VPS using its venv if possible, otherwise system python
    # We use nohup to keep it running
    vps_python = f"{vps_root}/venv/bin/python3"
    execute_cmd(ssh, f"ls {vps_python} || vps_python=python3")
    
    execute_cmd(ssh, f"cd {vps_root} && nohup python3 server.py > server.log 2>&1 &")
    
    print("DONE: Remote Deployment to /opt/noir-dashboard finished.")
    ssh.close()
    
except Exception as e:
    print(f"ERROR: {e}")
