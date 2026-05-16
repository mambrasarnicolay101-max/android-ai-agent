import asyncio
import websockets
import json
import subprocess
import os
import time

# CONFIGURATION
VPS_WS_URL = "ws://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"/ws/pc-bridge?device_id=REDMI_NOTE_14"
ADB_PATH = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"
DEVICE_SERIAL = "9LMBAUR4A6QG5TWW"
AUTH_TOKEN = "Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"

async def run_bridge():
    print(f"--- NOIR SOVEREIGN: ABSOLUTE PC BRIDGE ---")
    print(f"Connecting to VPS: {VPS_WS_URL}")
    
    while True:
        try:
            async with websockets.connect(VPS_WS_URL, extra_headers={"Authorization": AUTH_TOKEN}) as ws:
                print("CONNECTED! Listening for ADB commands...")
                
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    
                    if "commands" in data:
                        for cmd in data["commands"]:
                            cmd_id = cmd["command_id"]
                            action = cmd["action"]
                            
                            if action["type"] == "shell":
                                shell_cmd = action["cmd"]
                                print(f"Executing ADB: {shell_cmd}")
                                
                                # Run via ADB
                                full_cmd = f'"{ADB_PATH}" -s {DEVICE_SERIAL} shell "{shell_cmd}"'
                                try:
                                    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
                                    output = res.stdout if res.stdout else res.stderr
                                    print(f"Result: {output[:50]}...")
                                    
                                    # If it was a refresh/screenshot, we might need to pull the file
                                    if "screencap" in shell_cmd:
                                        pull_cmd = f'"{ADB_PATH}" -s {DEVICE_SERIAL} pull /sdcard/noir_shot.png noir_shot.png'
                                        subprocess.run(pull_cmd, shell=True)
                                        # Upload to VPS (simulated here, but the agent usually does it)
                                        # In Bridge mode, we can just use the direct PC-to-VPS upload
                                        print("Screenshot pulled to local.")
                                        
                                except Exception as e:
                                    print(f"ADB Error: {e}")
                                    
        except Exception as e:
            print(f"Bridge Error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_bridge())
