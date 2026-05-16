import paramiko
import os

hostname = "os.environ.get("NOIR_VPS_IP", "8.215.23.17")
username = "root"
password = "N!colay_No1r.Ai@Agent#Secure"
vps_root = "/root/noir-agent"

def execute_cmd(ssh, cmd):
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode().strip()

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    
    # 1. Kill everything
    print("--- Terminating old processes ---")
    execute_cmd(ssh, "pkill -f python3 || true")
    
    # 2. Start services with full absolute paths and proper redirection
    print("--- Launching Unified Sovereign Mesh ---")
    
    # Start Web Server (Foreground worker)
    # Using python3 -u to disable buffering
    cmd_web = f"cd {vps_root}/noir-ui && nohup python3 -u web_server.py --port 80 > /root/server_v2.log 2>&1 &"
    execute_cmd(ssh, cmd_web)
    
    # Start Shadow Node
    cmd_shadow = f"cd {vps_root}/noir-vps && nohup python3 -u shadow_node.py > /root/shadow_v2.log 2>&1 &"
    execute_cmd(ssh, cmd_shadow)
    
    # Start Grand Singularity Cycle
    cmd_evo = f"cd {vps_root}/noir-vps && nohup python3 -u grand_singularity_cycle.py > /root/evo_v2.log 2>&1 &"
    execute_cmd(ssh, cmd_evo)
    
    print("✅ Services launched. Verifying in 5 seconds...")
    import time
    time.sleep(5)
    
    processes = execute_cmd(ssh, "ps aux | grep python3 | grep -v grep")
    print(f"Active Processes:\n{processes}")
    
    ssh.close()
    
except Exception as e:
    print(f"❌ BOOTSTRAP FAILED: {e}")
