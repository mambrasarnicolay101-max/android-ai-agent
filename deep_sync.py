import paramiko
import os
import time

hostname = "os.environ.get("NOIR_VPS_IP", "8.215.23.17")
username = "root"
password = "N!colay_No1r.Ai@Agent#Secure"
vps_root = "/root/noir-agent"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    
    sftp = ssh.open_sftp()
    
    local_vps_dir = "c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/noir-vps"
    remote_vps_dir = f"{vps_root}/noir-vps"
    
    # 1. Sync EVERYTHING in noir-vps/
    print("--- Deep Syncing noir-vps/ folder to VPS ---")
    for fname in os.listdir(local_vps_dir):
        local_path = os.path.join(local_vps_dir, fname)
        if os.path.isfile(local_path):
            remote_path = f"{remote_vps_dir}/{fname}"
            print(f"Uploading {fname}...")
            sftp.put(local_path, remote_path)
            
    # 2. Sync noir-ui/ as well
    local_ui_dir = "c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/noir-ui"
    remote_ui_dir = f"{vps_root}/noir-ui"
    print("--- Deep Syncing noir-ui/ folder to VPS ---")
    for fname in os.listdir(local_ui_dir):
        local_path = os.path.join(local_ui_dir, fname)
        if os.path.isfile(local_path):
            remote_path = f"{remote_ui_dir}/{fname}"
            print(f"Uploading {fname}...")
            sftp.put(local_path, remote_path)
            
    sftp.close()
    
    # 3. Final Restart
    print("--- Final Mesh Reboot ---")
    ssh.exec_command("pkill -f python3 || true")
    time.sleep(2)
    ssh.exec_command(f"cd {vps_root}/noir-ui && nohup python3 web_server.py --port 80 > /root/server_v3.log 2>&1 &")
    ssh.exec_command(f"cd {vps_root}/noir-vps && nohup python3 shadow_node.py > /root/shadow_v3.log 2>&1 &")
    ssh.exec_command(f"cd {vps_root}/noir-vps && nohup python3 grand_singularity_cycle.py > /root/evo_v3.log 2>&1 &")
    
    print("✅ DEEP SYNC & REBOOT COMPLETE.")
    ssh.close()
    
except Exception as e:
    print(f"❌ DEEP SYNC ERROR: {e}")
