import os
import subprocess
import time
import sys

def setup_pc_bridge():
    print("""
    \033[96m=====================================================
    NOIR SOVEREIGN — AUTOMATED PC BRIDGE v1.0
    =====================================================\033[0m
    """)
    
    # 1. Check for ADB
    print("[\033[94mINFO\033[0m] Verifying ADB connection to Redmi Note 14...")
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if "device" not in result.stdout.split('\n')[1]:
        print("[\033[91mERROR\033[0m] No Android device detected via USB. Please connect your Redmi Note 14.")
        return

    # 2. Setup ADB Reverse
    print("[\033[94mINFO\033[0m] Establishing Neural Tunnel (ADB Reverse Port 8080)...")
    subprocess.run(["adb", "reverse", "tcp:8080", "tcp:8080"])
    
    # 3. Launch PC Agent
    print("[\033[92mREADY\033[0m] Launching PC Agent Listener...")
    if os.path.exists("pc_agent.py"):
        try:
            subprocess.run([sys.executable, "pc_agent.py"])
        except KeyboardInterrupt:
            print("\n[\033[93mWARNING\033[0m] Bridge closed.")
    else:
        print("[\033[91mERROR\033[0m] pc_agent.py not found in the current directory.")

if __name__ == "__main__":
    setup_pc_bridge()
