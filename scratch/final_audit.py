import os
import sys
from pathlib import Path

def audit_fixes():
    print("=== FINAL POST-FIX AUDIT ===")
    
    # 1. Check agent.py NameError fix
    agent_path = Path("noir-core/agent.py")
    if agent_path.exists():
        with open(agent_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Check if log is defined before use
            log_def = -1
            log_use = -1
            for i, line in enumerate(lines):
                if 'log = logging.getLogger' in line: log_def = i
                if 'log.error' in line and log_use == -1: log_use = i
            
            if log_def != -1 and log_use != -1 and log_def < log_use:
                print("[OK] agent.py: Logger initialized before use.")
            else:
                print("[FAIL] agent.py: Logger usage still potentially problematic.")

    # 2. Check hardcoded IP
    print("Checking for hardcoded IP '8.215.23.17'...")
    found_ip = False
    for root, dirs, files in os.walk("."):
        if 'venv' in root or '.git' in root or 'scratch' in root: continue
        for file in files:
            if file.endswith(('.py', '.js', '.ts')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        if '8.215.23.17' in f.read():
                            # Ignore the config_manager itself as it has it as default
                            if 'config_manager.py' not in file:
                                print(f"[WARN] Hardcoded IP still in {path}")
                                found_ip = True
                except: pass
    if not found_ip:
        print("[OK] No hardcoded IPs found (except in config/backups).")

    # 3. Check Knowledge Conflict
    sandbox_knowledge = Path(".sandbox/gold_master/knowledge")
    if not sandbox_knowledge.exists():
        print("[OK] Duplicate knowledge in .sandbox removed.")
    else:
        print("[FAIL] Duplicate knowledge still exists.")

    # 4. Check Thread Management
    orch_path = Path("noir-vps/sovereign_orchestrator.py")
    with open(orch_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if '_running_threads' in content and 'is_alive()' in content:
            print("[OK] Orchestrator thread management implemented.")
        else:
            print("[FAIL] Orchestrator still lacks thread management.")

if __name__ == "__main__":
    audit_fixes()
