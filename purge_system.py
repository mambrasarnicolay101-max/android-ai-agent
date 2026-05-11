import os
import shutil
import psutil
import time

def purge_junk():
    print("[PURGE] Starting deep system cleanup...")
    
    # 1. Clear __pycache__
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                print(f"  Removing {path}")
                shutil.rmtree(path, ignore_errors=True)

    # 2. Clear old logs and sandbox
    extra_dirs = ["logs", "noir-vps/.sandbox"]
    for d in extra_dirs:
        if os.path.exists(d):
            print(f"  Purging directory: {d}")
            shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    # 3. Remove legacy test scripts
    legacy_files = [
        "test_flow.py", "test_poll.py", "test_queue.py", 
        "test_upload.py", "test_upload_vps.py", "test_upload_data.py",
        "diagnose_ssl.py", "diagnose_ssl_file.py", "diagnose_ssl_final.py",
        "ssl_report.txt", "ssl_report_final.txt", "test2.txt", "test_upload.py",
        "AUDIT_REPORT.md", "AUDIT_REPORT_V17.md", "inventory_report.json", "summary.json",
        "deploy_vps.py", "full_deploy.py", "final_deploy.py", "docker_run_deploy.py",
        "audit_vps.py", "fix_deps.py", "packages.txt"
    ]
    for f in legacy_files:
        if os.path.exists(f):
            print(f"  Deleting legacy file: {f}")
            os.remove(f)

    print("[PURGE] Cleanup complete.")

def ensure_single_command():
    print("[SINGLE-CMD] Ensuring absolute process sovereignty...")
    current_pid = os.getpid()
    
    # Target common Noir process names
    targets = ["brain.py", "web_server.py"]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = proc.info.get('cmdline')
            if cmd and any(t in " ".join(cmd) for t in targets):
                if proc.info['pid'] != current_pid:
                    print(f"  Killing redundant process: {proc.info['pid']} ({' '.join(cmd)})")
                    proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    print("[SINGLE-CMD] All redundant commands purged.")

if __name__ == "__main__":
    purge_junk()
    # ensure_single_command() # Only run if not in current session
