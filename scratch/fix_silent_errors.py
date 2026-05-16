import os
import re

def fix_silent_errors(file_path):
    if not os.path.exists(file_path): return
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Replace 'except: pass' or 'except Exception: pass' with logging
    # We use a lambda to maintain indentation if possible, but for simplicity:
    new_content = re.sub(r'except:\s+pass', 'except Exception as e:\n            log.debug(f"Silent error suppressed: {e}")', content)
    new_content = re.sub(r'except Exception:\s+pass', 'except Exception as e:\n            log.debug(f"Silent error suppressed: {e}")', new_content)
    
    if new_content != content:
        print(f"Fixed silent errors in {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

if __name__ == "__main__":
    # Fix core files
    fix_silent_errors("noir-ui/web_server.py")
    fix_silent_errors("noir-vps/brain.py")
    fix_silent_errors("noir-vps/sovereign_orchestrator.py")
    fix_silent_errors("noir-core/agent.py")
