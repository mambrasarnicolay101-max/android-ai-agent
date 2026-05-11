import threading
import subprocess
import time
import os
import sys

def run_purge():
    print("[BOOT] Purging legacy caches and junk...")
    subprocess.run([sys.executable, "purge_system.py"], check=True)

def start_web_server():
    print("[BOOT] Launching Noir Sovereign Web Server (Port 8765)...")
    # Using subprocess to keep it isolated but manageable
    subprocess.run([sys.executable, "noir-ui/web_server.py"])

def start_brain_engine():
    print("[BOOT] Synchronizing Neural Brain Engine...")
    subprocess.run([sys.executable, "noir-vps/brain.py"])

def start_neural_reflex():
    print("[BOOT] Activating Neural Reflex (Real-time Anomaly Detection)...")
    subprocess.run([sys.executable, "noir-vps/neural_reflex.py"])

if __name__ == "__main__":
    print("=======================================================")
    print("   NOIR SOVEREIGN - SINGLE COMMAND SOVEREIGNTY BOOT")
    print("=======================================================")
    
    run_purge()
    
    # Start Web Server in background thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    
    # Start Neural Reflex in background thread
    reflex_thread = threading.Thread(target=start_neural_reflex, daemon=True)
    reflex_thread.start()
    
    # Wait for server to warm up
    time.sleep(3)
    
    # Start Brain Engine in main thread (blocks until exit)
    try:
        start_brain_engine()
    except KeyboardInterrupt:
        print("\n[BOOT] System shutdown sequence initiated...")
        sys.exit(0)
