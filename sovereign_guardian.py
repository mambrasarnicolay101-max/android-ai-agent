import time
import subprocess
import os
import requests
import json
from datetime import datetime

# CONFIGURATION
ADB_PATH = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"
DEVICE_IP = "192.168.1.32"
VPS_HEALTH_URL = "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+":8765/health"
DEVICE_SERIAL = f"{DEVICE_IP}:5555"

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [GUARDIAN] {msg}")

import shlex

def run_adb(cmd):
    try:
        # Menghindari command injection dengan menggunakan list of arguments
        base_cmd = [ADB_PATH, "-s", DEVICE_SERIAL]
        args = shlex.split(cmd)
        full_cmd = base_cmd + args
        result = subprocess.run(full_cmd, shell=False, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        log(f"ERROR executing adb: {str(e)}")
        return f"ERROR: {str(e)}"

def check_device_online():
    # Check if adb sees the device
    out = subprocess.run(f'"{ADB_PATH}" devices', shell=True, capture_output=True, text=True).stdout
    if DEVICE_SERIAL in out:
        return True
    # Try to reconnect
    log(f"Device {DEVICE_SERIAL} not found in adb. Attempting reconnect...")
    subprocess.run(f'"{ADB_PATH}" connect {DEVICE_SERIAL}', shell=True)
    time.sleep(2)
    out = subprocess.run(f'"{ADB_PATH}" devices', shell=True, capture_output=True, text=True).stdout
    return DEVICE_SERIAL in out

def check_service_running():
    ps = run_adb("shell ps -A")
    return "com.noir.aegis" in ps

def revive_agent():
    log("💀 Agent seems dead. Executing Phoenix Revival...")
    run_adb("shell am force-stop com.noir.aegis")
    time.sleep(1)
    run_adb("shell am start -n com.noir.aegis/.MainActivity")
    log("🚀 Agent restarted.")

def main_loop():
    log("Noir Sovereign Guardian Started - Monitoring Node: " + DEVICE_SERIAL)
    
    while True:
        try:
            # 1. Check ADB Connectivity
            if not check_device_online():
                log("X Device unreachable via ADB. Check WiFi/IP.")
            else:
                # 2. Check Service Process
                if not check_service_running():
                    log("! Aegis process not found.")
                    revive_agent()
                else:
                    # 3. Check Shizuku status
                    ps = run_adb("shell ps -A")
                    if "shizuku_server" not in ps:
                        log("Shizuku server dead. Restarting...")
                        run_adb("shell am start -n moe.shizuku.privileged.api/.MainActivity")
                        # Note: Shizuku might need manual start click, but opening the app helps.
                    
            # 4. Check VPS connectivity (Optional from PC side)
            try:
                r = requests.get(VPS_HEALTH_URL, timeout=5)
                if r.status_code == 200:
                    pass # VPS is up
            except:
                log("🌐 VPS Health check failed. Ensure web_server.py is running on Alibaba.")

        except Exception as e:
            log(f"Critical Loop Error: {str(e)}")
            
        time.sleep(30) # Monitor every 30 seconds

if __name__ == "__main__":
    main_loop()
