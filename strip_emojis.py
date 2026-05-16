import os
import re

def remove_emojis(text):
    # This regex matches common emojis and special characters that cause encoding issues
    return re.sub(r'[^\x00-\x7f]', r'', text)

root_dir = "c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/noir-vps"

print("--- Stripping Emojis from noir-vps/ for VPS compatibility ---")

for fname in os.listdir(root_dir):
    if fname.endswith(".py"):
        path = os.path.join(root_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        clean_content = remove_emojis(content)
        
        if content != clean_content:
            print(f"Cleaned {fname}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(clean_content)

print("✅ Emojis stripped. Ready for VPS Sync.")
