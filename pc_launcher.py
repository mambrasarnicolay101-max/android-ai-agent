#!/usr/bin/env python3
"""
NOIR SOVEREIGN PC LAUNCHER v21.2 [ELITE AEGIS MODE]
===================================================
Membungkus Dashboard Web menjadi Aplikasi Desktop Windows
menggunakan PyWebView — tanpa memerlukan browser terpisah.

Cara menjalankan:
    pip install pywebview psutil
    python pc_launcher.py

Atau build menjadi .exe:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "Noir Sovereign" pc_launcher.py
"""

import os, sys, subprocess, threading, time, logging
from pathlib import Path

log = logging.getLogger("Launcher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [LAUNCHER] %(message)s")

BASE_DIR = Path(__file__).resolve().parent

# ─── KONFIGURASI LAUNCHER ────────────────────────────────────────────────────
SERVER_HOST   = "127.0.0.1"
SERVER_PORT   = 8765          # Port khusus mode Desktop agar tidak bentrok

# Ambil Gateway dari ENV jika ada (untuk koneksi ke VPS Remote)
GATEWAY_URL   = os.environ.get("NOIR_GATEWAY_URL", f"http://{SERVER_HOST}:{SERVER_PORT}").rstrip("/")
SERVER_URL    = GATEWAY_URL

WINDOW_TITLE  = "Noir Sovereign — PC Commander"
WINDOW_W      = 1280
WINDOW_H      = 820
WINDOW_MIN_W  = 900
WINDOW_MIN_H  = 600

# ─── STEP 1: START WEB SERVER DI BACKGROUND THREAD ──────────────────────────
def _start_server():
    """Jalankan web_server.py sebagai proses background."""
    server_path = BASE_DIR / "noir-ui" / "web_server.py"
    if not server_path.exists():
        log.error(f"web_server.py tidak ditemukan di: {server_path}")
        sys.exit(1)

    if "localhost" in SERVER_URL or "127.0.0.1" in SERVER_URL:
        log.info(f"Starting Local Web Server at {SERVER_URL}...")
        env = os.environ.copy()
        env["NOIR_PC_MODE"]   = "1"          # Flag mode Desktop
        env["NOIR_PC_PORT"]   = str(SERVER_PORT)
        subprocess.Popen(
            [sys.executable, str(server_path), "--port", str(SERVER_PORT)],
            cwd=str(BASE_DIR),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        log.info(f"Connecting to Remote VPS: {SERVER_URL}")

def _wait_for_server(timeout: int = 15) -> bool:
    """Tunggu hingga server siap menerima koneksi."""
    import urllib.request, urllib.error
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{SERVER_URL}/health", timeout=1)
            log.info("Server Ready.")
            return True
        except:
            time.sleep(0.4)
    return False

# ─── STEP 2: START BRAIN/AUTONOMOUS LOOP DI BACKGROUND ──────────────────────
def _start_brain():
    """Jalankan otak AI (brain.py) dalam background thread terpisah."""
    if not ("localhost" in SERVER_URL or "127.0.0.1" in SERVER_URL):
        log.info("Brain already running on VPS. Skipping local start.")
        return

    brain_path = BASE_DIR / "noir-vps" / "brain.py"
    if not brain_path.exists():
        log.warning("brain.py tidak ditemukan. Lewati.")
        return

    log.info("Memulai Noir Brain (Autonomous PC Mode)...")
    subprocess.Popen(
        [sys.executable, str(brain_path)],
        cwd=str(BASE_DIR / "noir-vps"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# ─── STEP 3: BUKA JENDELA DESKTOP DENGAN PYWEBVIEW ──────────────────────────
def _launch_window():
    """Buka jendela desktop menggunakan PyWebView."""
    try:
        import webview
    except ImportError:
        log.error("PyWebView tidak terinstal! Jalankan: pip install pywebview")
        # Fallback: Buka browser biasa
        import webbrowser
        webbrowser.open(SERVER_URL)
        log.info(f"Dashboard dibuka di browser: {SERVER_URL}")
        input("Tekan Enter untuk keluar...")
        return

    log.info(f"Opening Desktop Window: {WINDOW_TITLE}")

    # Tambahkan JS bridge untuk interaksi Python-JS
    class JsBridge:
        """API yang bisa dipanggil dari JavaScript dashboard."""
        
        def get_pc_stats(self):
            """Ambil statistik PC dari Python langsung."""
            try:
                sys.path.insert(0, str(BASE_DIR / "noir-vps"))
                from pc_executor import PCExecutor
                stats = PCExecutor.get_system_stats()
                import json
                return json.dumps(stats)
            except Exception as e:
                return f'{{"error": "{e}"}}'

        def run_pc_command(self, cmd: str):
            """Jalankan perintah shell di PC dari Dashboard."""
            try:
                sys.path.insert(0, str(BASE_DIR / "noir-vps"))
                from pc_executor import PCExecutor
                result = PCExecutor.run_shell(cmd)
                import json
                return json.dumps(result)
            except Exception as e:
                return f'{{"error": "{e}"}}'

        def minimize(self):
            webview.windows[0].minimize()

        def maximize(self):
            w = webview.windows[0]
            if w.maximized:
                w.restore()
            else:
                w.maximize()

        def close(self):
            webview.windows[0].destroy()

    bridge = JsBridge()

    window = webview.create_window(
        title    = WINDOW_TITLE,
        url      = SERVER_URL,
        width    = WINDOW_W,
        height   = WINDOW_H,
        min_size = (WINDOW_MIN_W, WINDOW_MIN_H),
        resizable= True,
        js_api   = bridge,
        frameless= False,            # Gunakan True jika ingin tampilan fullscreen edge-to-edge
        easy_drag= False,
        background_color= "#0a0a0f"  # Warna background saat loading (hitam noir)
    )

    webview.start(
        debug   = False,
        http_server= False,          # Server sudah kita jalankan manual
        gui     = "edgechromium"     # Gunakan Chromium bawaan Windows (Edge) agar stabil
    )

# ─── MAIN ENTRY POINT ────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  [NOIR SOVEREIGN] PC COMMANDER v1.0")
    print("  Mode: AUTONOMOUS DESKTOP APPLICATION")
    print("=" * 60)

    # 1. Mulai server dan brain di background
    threading.Thread(target=_start_server, daemon=True).start()
    time.sleep(1)  # Beri jeda kecil sebelum cek status
    threading.Thread(target=_start_brain, daemon=True).start()

    # 2. Tunggu server siap
    log.info("Waiting for server...")
    ready = _wait_for_server(timeout=20)
    if not ready:
        log.error("Server gagal start dalam 20 detik. Coba jalankan manual: uvicorn noir-ui/web_server:app")
        # Tetap buka jendela — user bisa refresh
        
    # 3. Buka jendela Desktop
    _launch_window()

    log.info("Noir Sovereign Desktop App closed.")

if __name__ == "__main__":
    main()
