import os
import re

TARGET_IP = "os.environ.get("NOIR_VPS_IP", "8.215.23.17")
REPLACEMENT = "NoirConfig.VPS_IP" # Note: This requires the file to import NoirConfig

# For files that don't use the config yet, we can at least make them use os.environ
def harden_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Replace hardcoded IP in strings/configs
    new_content = content.replace(TARGET_IP, '"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"')
    
    # Clean up double-double quotes if they occur
    new_content = new_content.replace('"', '"')
    new_content = new_content.replace('', '')
    
    if new_content != content:
        print(f"Hardening {file_path}...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

def scan_and_harden(root_dir):
    for root, dirs, files in os.walk(root_dir):
        if '.git' in dirs: dirs.remove('.git')
        if 'venv' in dirs: dirs.remove('venv')
        
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.h', '.ps1')):
                harden_file(os.path.join(root, file))

if __name__ == "__main__":
    scan_and_harden(".")
