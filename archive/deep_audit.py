import os
import paramiko, os, time
from dotenv import load_dotenv

load_dotenv()

def deep_audit():
    print("--- NOIR SOVEREIGN DEEP SYSTEM AUDIT ---")
    
    # 1. VPS AUDIT
    print("\n[1] AUDITING ALIBABA VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(os.environ['NOIR_VPS_IP'], username=os.environ['NOIR_VPS_USER'], password=os.environ['NOIR_VPS_PASS'])
        
        # Check processes
        _, stdout, _ = ssh.exec_command("ps aux | grep -E 'uvicorn|web_server' | grep -v grep")
        procs = stdout.read().decode().strip()
        if procs:
            print(f"OK SERVER PROCESSES FOUND:\n{procs}")
        else:
            print("ERROR: NO SERVER PROCESSES RUNNING!")

        # Check port 80
        _, stdout, _ = ssh.exec_command("netstat -tuln | grep :80")
        port80 = stdout.read().decode().strip()
        if port80:
            print(f"OK PORT 80 IS LISTENING:\n{port80}")
        else:
            print("ERROR: PORT 80 IS NOT LISTENING!")

        # Check local_state (via a small script)
        check_state_cmd = """python3 -c 'import sys; sys.path.append("/root/noir-agent/noir-ui"); from web_server import local_state, active_websockets; print(f"Agents: {list(local_state[\\"agents\\"].keys())}"); print(f"WS Active: {list(active_websockets.keys())}")'"""
        _, stdout, stderr = ssh.exec_command(check_state_cmd)
        print(f"VPS AGENT STATE: {stdout.read().decode().strip()}")
        err = stderr.read().decode().strip()
        if err: print(f"WARNING State Check Error: {err}")

    except Exception as e:
        print(f"ERROR VPS SSH FAILURE: {str(e)}")
    finally:
        ssh.close()

    # 2. ANDROID AUDIT (via ADB)
    print("\n[2] AUDITING REDMI NOTE 14 (via ADB)...")
    adb = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"
    sn = "9LMBAUR4A6QG5TWW"
    
    def run_adb(cmd):
        import subprocess
        res = subprocess.run(f'"{adb}" -s {sn} {cmd}', shell=True, capture_output=True, text=True)
        return res.stdout.strip()

    # Check Shizuku
    shizuku = run_adb("shell ps -A | grep shizuku")
    if shizuku:
        print(f"OK SHIZUKU PROCESS: {shizuku}")
    else:
        print("ERROR: SHIZUKU IS NOT RUNNING!")

    # Check Aegis Service
    aegis = run_adb("shell dumpsys activity services com.noir.aegis")
    if "AegisService" in aegis:
        print("OK AEGIS SERVICE IS RUNNING")
    else:
        print("ERROR: AEGIS SERVICE IS NOT RUNNING!")

    # Check Connection Logs
    logs = run_adb("logcat -d -s NeuralLink | tail -n 10")
    print(f"LOGS NEURALLINK:\n{logs}")

if __name__ == "__main__":
    deep_audit()

