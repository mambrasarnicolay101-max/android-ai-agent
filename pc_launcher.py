#!/usr/bin/env python3
"""
NOIR SOVEREIGN PC COMMANDER v21.4 [EDGE APP MODE]
==================================================
Membuka Dashboard VPS Alibaba di Microsoft Edge dalam
mode "App Window" — tampilan native tanpa browser bar.

Cara menjalankan:
    python pc_launcher.py

Build EXE:
    pyinstaller --onefile --windowed --name "Noir Sovereign" --exclude-module setuptools pc_launcher.py
"""

import os, sys, time, json, subprocess, logging, threading
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [NOIR] %(message)s")
log = logging.getLogger("NoirLauncher")

# ─── KONFIGURASI ──────────────────────────────────────────────────────────────
VPS_IP   = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_URL  = os.environ.get("NOIR_GATEWAY_URL", f"http://{VPS_IP}").rstrip("/")

# ─── EDGE APP MODE PATHS (Windows 10/11) ─────────────────────────────────────
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
]

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]

def _find_browser() -> tuple[str, str]:
    """Cari Edge atau Chrome yang tersedia di sistem."""
    for path in EDGE_PATHS:
        if os.path.exists(path):
            return path, "edge"
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path, "chrome"
    return "", "none"

# ─── CEK KONEKTIVITAS VPS ─────────────────────────────────────────────────────
def _check_vps() -> bool:
    import urllib.request
    try:
        r = urllib.request.urlopen(f"{VPS_URL}/health", timeout=8)
        data = json.loads(r.read().decode())
        log.info(f"VPS ONLINE — {data.get('version','?')} | Mesh: {data.get('mesh','?')}")
        return True
    except Exception as e:
        log.error(f"VPS tidak dapat dijangkau: {e}")
        return False

# ─── SPLASH SCREEN (TKinter minimal) ─────────────────────────────────────────
def _show_splash_and_open():
    """Tampilkan splash Tkinter lalu buka Edge App Mode."""
    try:
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.title("Noir Sovereign")
        root.geometry("480x300")
        root.configure(bg="#0a0a0f")
        root.resizable(False, False)
        root.overrideredirect(True)  # tanpa window border

        # Posisi tengah layar
        w, h = 480, 300
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        # UI Splash
        tk.Label(root, text="NOIR SOVEREIGN", font=("Segoe UI", 22, "bold"),
                 fg="#7c3aed", bg="#0a0a0f").pack(pady=(40, 5))
        tk.Label(root, text="AI Agent Command Center", font=("Segoe UI", 11),
                 fg="#888", bg="#0a0a0f").pack()
        tk.Label(root, text=f"VPS: {VPS_IP}", font=("Segoe UI", 10),
                 fg="#05ffa1", bg="#0a0a0f").pack(pady=5)

        status_var = tk.StringVar(value="Memeriksa konektivitas VPS...")
        tk.Label(root, textvariable=status_var, font=("Segoe UI", 9),
                 fg="#aaa", bg="#0a0a0f").pack(pady=(20, 5))

        bar = ttk.Progressbar(root, length=300, mode="indeterminate")
        bar.pack(pady=10)
        bar.start(10)

        def _run_check():
            online = _check_vps()
            if online:
                status_var.set("VPS Online! Membuka dashboard...")
                time.sleep(0.8)
                root.after(100, lambda: _open_dashboard(root))
            else:
                bar.stop()
                status_var.set(f"Gagal terhubung ke {VPS_IP}. Periksa koneksi internet.")
                tk.Label(root, text="Tekan ESC untuk keluar", font=("Segoe UI", 9),
                         fg="#ff4444", bg="#0a0a0f").pack()
                root.bind("<Escape>", lambda e: root.destroy())

        threading.Thread(target=_run_check, daemon=True).start()
        root.mainloop()

    except ImportError:
        # Tkinter tidak tersedia (jarang di Windows), langsung buka
        if _check_vps():
            _open_dashboard(None)
        else:
            print(f"[ERROR] VPS tidak dapat dijangkau: {VPS_URL}")
            sys.exit(1)

def _open_dashboard(root_window):
    """Buka VPS dashboard di Edge/Chrome App Mode atau browser default."""
    browser_path, browser_type = _find_browser()

    if browser_path:
        # App mode = window native tanpa browser bar (persis seperti desktop app)
        app_args = [
            browser_path,
            f"--app={VPS_URL}",
            "--window-size=1400,860",
            "--disable-extensions",
            "--no-first-run",
        ]
        log.info(f"Membuka dengan {browser_type} App Mode: {VPS_URL}")
        subprocess.Popen(app_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        # Ultimate fallback: browser default
        import webbrowser
        log.info(f"Membuka dengan browser default: {VPS_URL}")
        webbrowser.open(VPS_URL)

    if root_window:
        root_window.after(500, root_window.destroy)

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  NOIR SOVEREIGN — PC COMMANDER v21.4")
    print(f"  VPS Alibaba: {VPS_URL}")
    print("=" * 55)
    _show_splash_and_open()

if __name__ == "__main__":
    main()
