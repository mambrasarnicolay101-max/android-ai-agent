import os
import subprocess
import time
import sys

def launch_sovereign():
    print("""
    \033[95m=====================================================
    NOIR SOVEREIGN — SUPREME COMMAND LAUNCHER v3.1
    =====================================================\033[0m
    """)
    
    # 1. Integrity Check
    print("[\033[94mINFO\033[0m] Performing system integrity audit...")
    if not os.path.exists("noir-ui/web_server.py"):
        print("[\033[91mERROR\033[0m] Core components missing! Aborting.")
        return

    # 2. Cleanup
    print("[\033[94mINFO\033[0m] Purging legacy neural caches...")
    subprocess.run([sys.executable, "purge_system.py"], capture_output=True)

    # 3. Start Swarm Bus & Web Server
    print("[\033[92mREADY\033[0m] Booting Brain Engine & Mission Control Dashboard...")
    
    # Menjalankan web_server.py di background
    cmd = [sys.executable, "-m", "uvicorn", "noir-ui.web_server:app", "--host", "0.0.0.0", "--port", "80"]
    try:
        process = subprocess.Popen(cmd)
        print("[\033[92mSUCCESS\033[0m] Sovereign Dashboard is now ONLINE at http://8.215.23.17")
        print("[\033[94mINFO\033[0m] Waiting for Redmi Note 14 Agent to synchronize...")
        
        while True:
            time.sleep(10)
            # Logika monitoring status agent di sini
    except KeyboardInterrupt:
        print("\n[\033[93mWARNING\033[0m] Shutdown signal received. Hibernating Noir Sovereign...")
        process.terminate()

if __name__ == "__main__":
    launch_sovereign()
