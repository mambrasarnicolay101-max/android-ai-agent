import paramiko
import os
import time
from dotenv import load_dotenv
from scp import SCPClient

load_dotenv()

VPS_IP   = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS", "N!colay_No1r.Ai@Agent#Secure")
REMOTE_ROOT = "/root/noir-agent"

def exec_cmd(ssh, cmd, wait=True):
    _, stdout, stderr = ssh.exec_command(cmd)
    if wait:
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        return out, err
    return None, None

def deploy():
    print(f"=== NOIR SOVEREIGN DEPLOY v21.4 ===")
    print(f"Target: {VPS_IP}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS, timeout=15)
        print("Connected to VPS.")

        # 1. Sync files
        with SCPClient(ssh.get_transport()) as scp:
            print("Syncing .env...")
            scp.put(".env", remote_path=REMOTE_ROOT + "/.env")
            print("Syncing root scripts...")
            scripts = ["sovereign_unified_boot.py", "purge_system.py", "requirements.txt"]
            for s in scripts:
                if os.path.exists(s):
                    scp.put(s, remote_path=REMOTE_ROOT + "/" + s)
            print("Syncing noir-ui/...")
            scp.put("noir-ui", remote_path=REMOTE_ROOT, recursive=True)
            print("Syncing noir-vps/...")
            scp.put("noir-vps", remote_path=REMOTE_ROOT, recursive=True)

        # 2. Ensure python-multipart is installed (required for file upload endpoint)
        print("Ensuring dependencies are installed...")
        out, _ = exec_cmd(ssh, "pip3 install python-multipart websockets --quiet 2>&1 | tail -3")
        print(f"  Deps: {out[:80] if out else 'OK'}")

        # 3. Purge __pycache__ to avoid stale bytecode conflicts
        exec_cmd(ssh, f"find {REMOTE_ROOT} -type d -name __pycache__ -exec rm -rf {{}} + 2>/dev/null || true")
        print("Purged __pycache__ directories.")

        # 4. Kill ALL old server processes (both gunicorn AND uvicorn)
        print("Stopping all server processes...")
        exec_cmd(ssh, "pkill -9 -f gunicorn 2>/dev/null || true")
        exec_cmd(ssh, "pkill -9 -f uvicorn 2>/dev/null || true")
        exec_cmd(ssh, "pkill -9 -f web_server 2>/dev/null || true")
        exec_cmd(ssh, "fuser -k 80/tcp 2>/dev/null || true")
        time.sleep(2)

        # 5. Ensure screenshots directory exists
        exec_cmd(ssh, f"mkdir -p {REMOTE_ROOT}/noir-ui/screenshots")
        print("Screenshots directory ensured.")

        # 6. Start server — uvicorn ONLY (standardized, no gunicorn)
        print("Starting Noir Sovereign (uvicorn, port 80)...")
        start_cmd = (
            f"cd {REMOTE_ROOT}/noir-ui && "
            f"nohup python3 -m uvicorn web_server:app "
            f"--host 0.0.0.0 --port 80 --workers 1 "
            f"> server.log 2>&1 &"
        )
        exec_cmd(ssh, start_cmd, wait=False)
        time.sleep(5)

        # 7. Verify
        out, _ = exec_cmd(ssh, "netstat -tuln | grep :80")
        if out:
            print(f"SUCCESS: Server is LIVE on Port 80")
            print(f"  {out.strip()}")
        else:
            print("WARNING: Port 80 not detected. Checking logs...")
            log, _ = exec_cmd(ssh, f"tail -n 25 {REMOTE_ROOT}/noir-ui/server.log")
            print(f"Server Log:\n{log}")

        # 8. Final connectivity check
        out, _ = exec_cmd(ssh, "curl -s -o /dev/null -w '%{http_code}' http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"/")
        print(f"HTTP Health Check: {out} (expected: 200)")

    except Exception as e:
        print(f"DEPLOY ERROR: {str(e)}")
    finally:
        ssh.close()
        print("=== DEPLOY COMPLETE ===")

if __name__ == "__main__":
    deploy()
