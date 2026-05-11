"""
NOIR SOVEREIGN BACKGROUND SERVICE v17.1 SENTINEL
===============================================
Synchronized background engine with Autonomous Sentinel and Shizuku Bridge.
"""

import os
import time
import requests
import threading
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- CONFIG (Unified Standard v17.5 OMEGA-MESH) ---
# Forced to Direct VPS to reduce network contention
_BASE_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "http://8.215.23.17")
VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
FALLBACKS = [
    _BASE_GATEWAY,
    f"http://{VPS_IP}",
    f"http://{VPS_IP}:80",
    f"http://{VPS_IP}:8000",
]

class DynamicGateway:
    _current = None
    _last_discovery = 0
    @classmethod
    def get(cls):
        if cls._current and (time.time() - cls._last_discovery) < 300:
            return cls._current
        for gw in FALLBACKS:
            try:
                r = requests.get(f"{gw}/health", timeout=3)
                if r.status_code == 200:
                    cls._current = gw
                    cls._last_discovery = time.time()
                    return gw
            except: pass
        cls._current = None
        return _BASE_GATEWAY
    @classmethod
    def reset(cls):
        cls._current = None
        cls._last_discovery = 0

class _GatewayProxy:
    def __str__(self): return DynamicGateway.get()
    def __format__(self, format_spec): return format(str(self), format_spec)

GATEWAY_URL = _GatewayProxy()
API_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID   = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")
OFFLINE_LOG_FILE = os.path.join(os.path.dirname(__file__), "service_offline.log")

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

import queue
log_queue = queue.Queue()

def _log_worker():
    while True:
        try:
            msg = log_queue.get()
            session.post(
                f"{GATEWAY_URL}/agent/log",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"device_id": DEVICE_ID, "level": msg["level"], "message": f"[BG-SERVICE] {msg['message']}"},
                timeout=5
            )
        except: pass

threading.Thread(target=_log_worker, daemon=True).start()

def noir_log(message, level="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] [SERVICE-{level}] {message}"
    print(formatted_msg)
    
    # Persistent Offline Log
    try:
        with open(OFFLINE_LOG_FILE, "a") as f:
            f.write(formatted_msg + "\n")
    except: pass

    log_queue.put({"message": message, "level": level})

def run_service():
    noir_log("NOIR ELITE SERVICE v17.2.2 [OMEGA-FIX]: INITIALIZING...")
    
    # WARN-03 FIX: Kill old ghosts using updated package domain
    try:
        os.system("pkill -f org.noir.sovereign")
        os.system("pkill -f org.noir.agent")
    except: pass

    # WARN-01 FIX: Wait 6s for Android network init before first poll
    time.sleep(6)


    poll_interval = 10
    while True:
        try:
            # 1. Connectivity Check
            try:
                # FIX: Check Gateway directly instead of Google DNS
                r = session.get(f"{GATEWAY_URL}/health", timeout=3)
                is_online = r.status_code == 200
            except:
                is_online = False

            if not is_online:
                time.sleep(30)
                continue

            # 2. Adaptive Polling & Gateway Rotation
            headers = {"Authorization": f"Bearer {API_KEY}"}
            try:
                resp = session.get(
                    f"{GATEWAY_URL}/agent/poll",
                    headers=headers,
                    params={"device_id": DEVICE_ID, "client_type": "service"},
                    timeout=15
                )
            except:
                DynamicGateway.reset() # Rotate gateway on failure
                time.sleep(10)
                continue

            if resp.status_code == 200:
                data = resp.json()
                commands = data.get("commands", [])
                if commands:
                    noir_log(f"Received {len(commands)} background commands")
                    for cmd in commands:
                        try:
                            action = cmd.get("action", {})
                            atype = action.get("type", "")
                            if atype == "shell":
                                cmd_str = action.get("cmd", "")
                                noir_log(f"Executing BG Shell: {cmd_str}")
                                res = run_robust_shell(cmd_str)
                                session.post(
                                    f"{GATEWAY_URL}/agent/result",
                                    headers=headers,
                                    json={"command_id": cmd.get("command_id"), "device_id": DEVICE_ID, "success": res["success"], "output": res.get("output", "")},
                                    timeout=10
                                )
                        except Exception as e:
                            noir_log(f"BG Exec Error: {e}", level="ERROR")
                    poll_interval = 3 # Fast poll when active
                else:
                    # Adaptive Backoff: idle longer but check at least every 30s
                    poll_interval = min(poll_interval + 2, 30)
            
            time.sleep(poll_interval)
            
        except Exception as e:
            time.sleep(30)

def run_robust_shell(cmd, timeout=15):
    import subprocess
    # Detect Shizuku binary
    shizuku_binary = "shizuku"
    for path in ["shizuku", "/system/bin/shizuku", "/data/local/tmp/shizuku", "rish"]:
        try:
            if subprocess.run(f"{path} shell id", shell=True, capture_output=True, timeout=2).returncode == 0:
                shizuku_binary = path
                break
        except: continue
    
    final_cmd = f"{shizuku_binary} shell {cmd}" if "shizuku" in shizuku_binary or "rish" in shizuku_binary else cmd
    try:
        r = subprocess.run(final_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"success": r.returncode == 0, "output": (r.stdout + r.stderr).strip()}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    run_service()
