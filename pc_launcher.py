#!/usr/bin/env python3
"""
NOIR SOVEREIGN PC LAUNCHER v21.3 [VPS-DIRECT MODE]
===================================================
Membuka Dashboard Elite Noir Sovereign yang berjalan di VPS Alibaba
langsung di browser Windows (Edge/Chrome), tanpa memerlukan server lokal.

Cara menjalankan:
    python pc_launcher.py

Atau build menjadi .exe:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "Noir Sovereign" pc_launcher.py
"""

import os, sys, subprocess, threading, time, logging, webbrowser, json
from pathlib import Path

log = logging.getLogger("Launcher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [LAUNCHER] %(message)s")

BASE_DIR = Path(__file__).resolve().parent

# ─── KONFIGURASI VPS ──────────────────────────────────────────────────────────
VPS_HOST    = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_PORT    = 80
SERVER_URL  = os.environ.get("NOIR_GATEWAY_URL", f"http://{VPS_HOST}:{VPS_PORT}").rstrip("/")

WINDOW_TITLE = "Noir Sovereign — PC Commander"

# ─── CEK KONEKTIVITAS VPS ────────────────────────────────────────────────────
def _check_vps_connectivity(timeout: int = 8) -> bool:
    """Periksa apakah VPS Alibaba dapat dijangkau."""
    import urllib.request, urllib.error
    try:
        r = urllib.request.urlopen(f"{SERVER_URL}/health", timeout=timeout)
        data = json.loads(r.read().decode())
        log.info(f"[VPS ONLINE] Status: {data.get('status')} | Mode: {data.get('mode')} | Mesh: {data.get('mesh')}")
        return True
    except Exception as e:
        log.error(f"[VPS UNREACHABLE] Tidak dapat menjangkau {SERVER_URL}: {e}")
        return False

# ─── BUKA DASHBOARD VPS DI BROWSER ATAU WEBVIEW ──────────────────────────────
def _launch_window():
    """Buka jendela dashboard Noir Sovereign."""
    log.info(f"Opening Noir Sovereign Dashboard: {SERVER_URL}")

    # Coba buka dengan PyWebView (modus windowed app)
    try:
        import webview

        class JsBridge:
            """API yang dapat dipanggil dari JavaScript dashboard."""

            def get_pc_stats(self):
                try:
                    sys.path.insert(0, str(BASE_DIR / "noir-vps"))
                    from pc_executor import PCExecutor
                    return json.dumps(PCExecutor.get_system_stats())
                except Exception as e:
                    return json.dumps({"error": str(e)})

            def run_pc_command(self, cmd: str):
                try:
                    sys.path.insert(0, str(BASE_DIR / "noir-vps"))
                    from pc_executor import PCExecutor
                    return json.dumps(PCExecutor.run_shell(cmd))
                except Exception as e:
                    return json.dumps({"error": str(e)})

        bridge = JsBridge()

        window = webview.create_window(
            title           = WINDOW_TITLE,
            url             = SERVER_URL,
            width           = 1400,
            height          = 860,
            min_size        = (900, 600),
            resizable       = True,
            js_api          = bridge,
            background_color= "#0a0a0f",
        )

        log.info("Launching PyWebView window...")
        webview.start(debug=False)

    except ImportError:
        log.warning("PyWebView tidak terinstal. Membuka di browser default...")
        _open_in_browser()
    except Exception as e:
        log.warning(f"PyWebView gagal ({e}). Membuka di browser default...")
        _open_in_browser()

def _open_in_browser():
    """Fallback: buka dashboard di browser default Windows."""
    import subprocess
    log.info(f"Opening in default browser: {SERVER_URL}")
    try:
        # Coba Edge terlebih dahulu (standar Windows 10/11)
        subprocess.Popen(
            ["cmd", "/c", "start", "msedge", "--app=" + SERVER_URL + " --window-size=1400,860"],
            shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log.info("Dashboard dibuka di Microsoft Edge (app mode).")
    except Exception:
        # Fallback ke browser default
        webbrowser.open(SERVER_URL)
        log.info("Dashboard dibuka di browser default.")

    # Jaga proses tetap hidup agar exe tidak langsung tutup
    print("\n" + "=" * 60)
    print(f"  NOIR SOVEREIGN DASHBOARD")
    print(f"  Terhubung ke VPS Alibaba: {SERVER_URL}")
    print(f"  Tutup browser untuk keluar, atau tekan Ctrl+C di sini.")
    print("=" * 60)
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[SYSTEM] Noir Sovereign Desktop App closed.")
        sys.exit(0)

# ─── MAIN ENTRY POINT ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  NOIR SOVEREIGN — PC COMMANDER v21.3")
    print("  Target: VPS Alibaba Cloud")
    print(f"  Dashboard: {SERVER_URL}")
    print("=" * 60)

    # 1. Verifikasi konektivitas VPS
    log.info("Memeriksa konektivitas ke VPS Alibaba...")
    vps_online = _check_vps_connectivity()
    if not vps_online:
        print("\n[ERROR] VPS tidak dapat dijangkau. Periksa koneksi internet Anda.")
        print(f"  Target: {SERVER_URL}")
        input("Tekan Enter untuk keluar...")
        sys.exit(1)

    print(f"\n  [VPS ONLINE] Server aktif di {VPS_HOST}")
    print("  [LAUNCHING] Membuka Dashboard Elite...\n")

    # 2. Buka jendela dashboard
    _launch_window()

    log.info("Noir Sovereign Desktop App closed.")

if __name__ == "__main__":
    main()
