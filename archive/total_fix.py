import paramiko
import os

hostname = "os.environ.get("NOIR_VPS_IP", "8.215.23.17")
username = "root"
password = "N!colay_No1r.Ai@Agent#Secure"
vps_root = "/root/noir-agent" # Based on the audit ps output

def execute_cmd(ssh, cmd):
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    
    # 1. CLEANUP DISK SPACE
    print("--- Cleaning up VPS Disk Space ---")
    execute_cmd(ssh, "rm -rf /root/.cache/pip")
    execute_cmd(ssh, "find / -name '__pycache__' -type d -exec rm -rf {} +")
    execute_cmd(ssh, f"truncate -s 0 {vps_root}/noir-ui/server.log")
    execute_cmd(ssh, "apt-get clean")

    # 2. UPLOAD LATEST CORE LOGIC (Arms Race)
    print("--- Uploading Latest Arms Race Logic to VPS ---")
    sftp = ssh.open_sftp()
    local_base = "c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent"
    
    # Ensure directories exist
    try: sftp.mkdir(f"{vps_root}/noir-vps")
    except: pass
    
    files_to_sync = [
        ("noir-ui/index.html", f"{vps_root}/noir-ui/index.html"),
        ("noir-ui/web_server.py", f"{vps_root}/noir-ui/web_server.py"),
        ("noir-vps/ai_router.py", f"{vps_root}/noir-vps/ai_router.py"),
        ("noir-vps/shadow_node.py", f"{vps_root}/noir-vps/shadow_node.py"),
        ("noir-vps/grand_singularity_cycle.py", f"{vps_root}/noir-vps/grand_singularity_cycle.py"),
        ("knowledge/api_pool.json", f"{vps_root}/knowledge/api_pool.json"),
        (".env", f"{vps_root}/.env")
    ]
    
    for local_rel, vps_abs in files_to_sync:
        local_abs = os.path.join(local_base, local_rel)
        if os.path.exists(local_abs):
            sftp.put(local_abs, vps_abs)
            
    sftp.close()

    # 3. RESTART UNIFIED MESH
    print("--- Restarting Unified Sovereign Mesh on VPS ---")
    execute_cmd(ssh, "pkill -f python3 || true")
    
    # Start Web Server
    execute_cmd(ssh, f"cd {vps_root}/noir-ui && nohup python3 web_server.py --port 80 > server.log 2>&1 &")
    
    # Start Shadow Node (Watchdog)
    execute_cmd(ssh, f"cd {vps_root}/noir-vps && nohup python3 shadow_node.py > shadow.log 2>&1 &")
    
    # Start Grand Singularity (Evolution)
    execute_cmd(ssh, f"cd {vps_root}/noir-vps && nohup python3 grand_singularity_cycle.py > evolution.log 2>&1 &")

    print("DONE: Total Diagnosis & Fix Applied.")
    ssh.close()
    
except Exception as e:
    print(f"ERROR: {e}")
