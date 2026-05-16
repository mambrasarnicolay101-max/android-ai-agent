import os

def fix_syntax_errors(root_dir):
    pattern = 'os.environ.get("NOIR_VPS_IP", "8.215.23.17")'
    replacement = 'os.environ.get("NOIR_VPS_IP", "8.215.23.17")'
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    if pattern in content:
                        print(f"Fixing syntax error in {path}")
                        new_content = content.replace(pattern, replacement)
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    fix_syntax_errors(".")
