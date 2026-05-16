import paramiko
import json
import os

hostname = "os.environ.get("NOIR_VPS_IP", "8.215.23.17")
username = "root"
password = "N!colay_No1r.Ai@Agent#Secure"
vps_root = "/opt/noir-dashboard"

def execute_remote(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode().strip(), stderr.read().decode().strip()

print("[DIAGNOSIS] Starting Total Sovereign Audit...")

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    results = {}

    # 1. System Health
    results["uptime"], _ = execute_remote(ssh, "uptime")
    results["disk_usage"], _ = execute_remote(ssh, "df -h / | tail -1")
    results["memory"], _ = execute_remote(ssh, "free -m | grep Mem")

    # 2. Process Integrity
    results["processes"], _ = execute_remote(ssh, "ps aux | grep -E 'python|server.py|brain.py|shadow' | grep -v grep")

    # 3. Network & Connectivity
    results["listening_ports"], _ = execute_remote(ssh, "netstat -tulpn | grep LISTEN")
    results["api_connectivity"], _ = execute_remote(ssh, "curl -I -s --connect-timeout 5 https://dashscope-intl.aliyuncs.com | head -n 1")

    # 4. Error Logs Analysis
    results["server_errors"], _ = execute_remote(ssh, f"grep -i 'error' {vps_root}/server.log | tail -n 10")

    # 5. Database Health
    results["db_size"], _ = execute_remote(ssh, f"ls -lh {vps_root}/noir_sovereign.db")

    # Final Report
    print("\n" + "="*50)
    print("TOTAL AUDIT REPORT (VPS ALIBABA)")
    print("="*50)
    
    print(f"\n[RESOURCE HEALTH]")
    print(f"Uptime: {results['uptime']}")
    print(f"Disk Space: {results['disk_usage']}")
    print(f"RAM Usage (MB): {results['memory']}")

    print(f"\n[PROCESS INTEGRITY]")
    if results["processes"]:
        print(results["processes"])
    else:
        print("CRITICAL: No AI processes found running!")

    print(f"\n[NETWORK STATUS]")
    print(f"Listening Ports:\n{results['listening_ports']}")
    print(f"API Gateway Link: {results['api_connectivity'] or 'TIMEOUT/FAILED'}")

    print(f"\n[LOG FORENSICS]")
    if results["server_errors"]:
        print(f"Recent Server Errors:\n{results['server_errors']}")
    else:
        print("No critical server errors detected.")

    ssh.close()
    
except Exception as e:
    print(f"AUDIT FAILED: {e}")
