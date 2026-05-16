import subprocess
import time
import sys
import os
from multiprocessing import Process

def start_vps_brain():
    print("[\033[94mBRAIN\033[0m] Starting Sovereign Intelligence Core...")
    subprocess.run([sys.executable, "noir-vps/sovereign_orchestrator.py"])

def start_dashboard():
    print("[\033[92mDASHBOARD\033[0m] Launching Elite Mission Control (Sovereign Core)...")
    # Menggunakan web_server.py yang mendukung API dinamis
    subprocess.run([sys.executable, "noir-ui/web_server.py", "--port", "80"])

def start_pc_bridge():
    print("[\033[96mBRIDGE\033[0m] Establishing Neural PC Tunnel...")
    subprocess.run([sys.executable, "pc_bridge_launcher.py"])

def start_evolution_monitor():
    print("[\033[95mEVOLUTION\033[0m] Monitoring Agent Growth...")
    while True:
        # Logika monitoring perkembangan agen
        time.sleep(60)

if __name__ == "__main__":
    print("""
    \033[91m=====================================================
    NOIR SOVEREIGN — UNIFIED COMMAND SYSTEM v3.0
    =====================================================\033[0m
    """)
    
    processes = [
        Process(target=start_vps_brain),
        Process(target=start_dashboard),
        Process(target=start_pc_bridge)
    ]

    for p in processes:
        p.start()

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n[\033[93mSYSTEM\033[0m] Sovereign Hibernation Initiated.")
        for p in processes:
            p.terminate()
