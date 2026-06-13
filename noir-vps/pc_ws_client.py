"""
NOIR PC WEBSOCKET CLIENT v2.0
================================
Menghubungkan laptop ke web_server.py via WebSocket.
Ketika ReAct Agent mengirim tool_call, client ini mengeksekusinya di PC lokal.

Jalankan: python noir-vps/pc_ws_client.py
"""
import asyncio
import json
import os
import subprocess
import sys
import time
import threading

try:
    import websockets
except ImportError:
    print("[PC-WS] Menginstal websockets...")
    subprocess.run([sys.executable, "-m", "pip", "install", "websockets"], check=True)
    import websockets

SERVER_URL = "ws://127.0.0.1:8000/ws/pc_agent?device_id=LAPTOP_MASTER"
RECONNECT_DELAY = 5  # detik

# ─── TOOL EXECUTOR ────────────────────────────────────────────────────────────

def _exec_run_cmd(cmd: str, timeout: int = 30) -> str:
    """Jalankan shell command di PC lokal."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR] {result.stderr}"
        return output.strip() or "[OK] Perintah selesai tanpa output."
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Perintah '{cmd}' melebihi batas waktu {timeout}s."
    except Exception as e:
        return f"[ERROR] {e}"


def _exec_write_file(path: str, content: str) -> str:
    """Tulis konten ke file di PC lokal."""
    try:
        # Resolve relative path dari direktori project
        if not os.path.isabs(path):
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            path = os.path.join(base, path)
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[OK] File ditulis ke: {path}"
    except Exception as e:
        return f"[ERROR] Gagal menulis file: {e}"


def _exec_read_file(path: str) -> str:
    """Baca konten file di PC lokal."""
    try:
        if not os.path.isabs(path):
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            path = os.path.join(base, path)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(8192)  # max 8KB
        return content
    except Exception as e:
        return f"[ERROR] Gagal membaca file: {e}"


def _exec_sys_info() -> str:
    """Ambil info sistem PC."""
    try:
        import platform
        info = {
            "os": platform.system(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": sys.version,
            "cwd": os.getcwd(),
            "user": os.environ.get("USERNAME", "unknown"),
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"[ERROR] {e}"


def _exec_open_browser(url: str) -> str:
    """Buka URL di browser default."""
    try:
        import webbrowser
        webbrowser.open(url)
        return f"[OK] Browser dibuka: {url}"
    except Exception as e:
        return f"[ERROR] Gagal membuka browser: {e}"


def _exec_list_dir(path: str = ".") -> str:
    """List isi direktori."""
    try:
        if not os.path.isabs(path):
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            path = os.path.join(base, path)
        entries = []
        for item in os.listdir(path):
            full = os.path.join(path, item)
            size = os.path.getsize(full) if os.path.isfile(full) else "-"
            kind = "DIR" if os.path.isdir(full) else "FILE"
            entries.append(f"[{kind}] {item} ({size})")
        return "\n".join(entries) if entries else "[EMPTY DIR]"
    except Exception as e:
        return f"[ERROR] {e}"


TOOL_MAP = {
    "run_cmd":      lambda k: _exec_run_cmd(k.get("cmd", ""), k.get("timeout", 30)),
    "write_file":   lambda k: _exec_write_file(k.get("path", "output.txt"), k.get("content", "")),
    "read_file":    lambda k: _exec_read_file(k.get("path", "")),
    "sys_info":     lambda k: _exec_sys_info(),
    "open_browser": lambda k: _exec_open_browser(k.get("url", "")),
    "list_dir":     lambda k: _exec_list_dir(k.get("path", ".")),
}


def execute_tool(tool_name: str, kwargs: dict) -> str:
    """Dispatch tool execution."""
    handler = TOOL_MAP.get(tool_name)
    if not handler:
        return f"[ERROR] Tool tidak dikenal: '{tool_name}'. Tersedia: {list(TOOL_MAP.keys())}"
    try:
        return handler(kwargs)
    except Exception as e:
        return f"[ERROR] Tool '{tool_name}' crash: {e}"


# ─── WEBSOCKET CLIENT ─────────────────────────────────────────────────────────

async def run_client():
    print(f"\n[PC-WS] [CONNECTING] Menghubungkan ke {SERVER_URL}...")
    
    while True:
        try:
            async with websockets.connect(
                SERVER_URL,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=5,
            ) as ws:
                print(f"[PC-WS] [OK] TERHUBUNG! Laptop LAPTOP_MASTER siap menerima perintah.")
                print(f"[PC-WS]      Server: {SERVER_URL}")
                print(f"[PC-WS]      Tools : {list(TOOL_MAP.keys())}\n")

                async for message in ws:
                    try:
                        payload = json.loads(message)
                        msg_type = payload.get("type")

                        if msg_type == "tool_call":
                            req_id    = payload.get("req_id", "")
                            tool_name = payload.get("tool", "")
                            kwargs    = payload.get("kwargs", {})

                            print(f"[PC-WS] [TOOL] {tool_name}({kwargs})")
                            
                            # Jalankan di thread terpisah agar tidak memblokir event loop
                            loop = asyncio.get_event_loop()
                            result = await loop.run_in_executor(
                                None, execute_tool, tool_name, kwargs
                            )
                            
                            print(f"[PC-WS] [RESULT] [{req_id[:8]}]: {str(result)[:120]}...")

                            await ws.send(json.dumps({
                                "type":   "tool_result",
                                "req_id": req_id,
                                "result": result,
                            }))

                        elif msg_type == "ping":
                            await ws.send(json.dumps({"type": "pong"}))

                    except json.JSONDecodeError as e:
                        print(f"[PC-WS] [WARN] JSON error: {e}")
                    except Exception as e:
                        print(f"[PC-WS] [WARN] Error memproses pesan: {e}")

        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"[PC-WS] [DISCONNECTED] Koneksi terputus: {e}. Mencoba ulang dalam {RECONNECT_DELAY}s...")
            await asyncio.sleep(RECONNECT_DELAY)
        except OSError as e:
            print(f"[PC-WS] [WAIT] Server belum siap: {e}. Mencoba ulang dalam {RECONNECT_DELAY}s...")
            await asyncio.sleep(RECONNECT_DELAY)
        except Exception as e:
            print(f"[PC-WS] [ERROR] Error tidak terduga: {e}. Mencoba ulang dalam {RECONNECT_DELAY}s...")
            await asyncio.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    print("=" * 60)
    print(" NOIR PC WEBSOCKET CLIENT v2.0")
    print(" Hubungkan laptop ke Noir Sovereign Server")
    print("=" * 60)
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\n[PC-WS] Client dihentikan oleh pengguna.")
