import requests
import base64
import os

TOKEN = "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"
REPO = "mambrasarnicky1-lgtm/android-ai-agent"
BRANCH = "main"

FILES_TO_SYNC = [
    "noir-android-native/app/src/main/AndroidManifest.xml",
    "noir-android-native/app/src/main/java/com/noir/aegis/MainActivity.java",
    "noir-android-native/app/src/main/java/com/noir/aegis/CommandDispatcher.java",
    "noir-android-native/app/src/main/java/com/noir/aegis/AegisAccessibilityService.java",
    "noir-android-native/app/src/main/java/com/noir/aegis/SovereignEvolutionEngine.java",
    "noir-android-native/app/src/main/java/com/noir/aegis/SecurityAuditSkill.java",
    "noir-android-native/app/src/main/res/xml/accessibility_service_config.xml",
    "noir-android-native/app/src/main/res/xml/device_admin_info.xml",
    "noir-android-native/app/src/main/res/values/strings.xml"
]

def sync_file(path):
    url = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"Authorization": f"token {TOKEN}"}
    
    # Get current file SHA if exists
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
        
    data = {
        "message": f"Sovereign Upgrade: Sync {os.path.basename(path)}",
        "content": content,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha
        
    r = requests.put(url, json=data, headers=headers)
    if r.status_code in [200, 201]:
        print(f"✅ Synced: {path}")
    else:
        print(f"❌ Failed {path}: {r.json()}")

if __name__ == "__main__":
    for f in FILES_TO_SYNC:
        if os.path.exists(f):
            sync_file(f)
        else:
            print(f"⚠️ Skip (not found): {f}")
