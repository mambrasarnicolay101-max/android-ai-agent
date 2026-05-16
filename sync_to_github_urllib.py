import urllib.request
import json
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
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "NoirAgent"
    }
    
    # 1. Get SHA if exists
    sha = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            sha = res_data.get("sha")
    except Exception as e:
        pass

    # 2. Read local file
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # 3. Push update
    data = {
        "message": f"Sovereign Upgrade: Sync {os.path.basename(path)}",
        "content": content,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="PUT")
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201]:
                print(f"SUCCESS Synced: {path}")
    except Exception as e:
        print(f"FAILED {path}: {str(e)}")

if __name__ == "__main__":
    for f in FILES_TO_SYNC:
        if os.path.exists(f):
            sync_file(f)
        else:
            print(f"⚠️ Skip (not found): {f}")
