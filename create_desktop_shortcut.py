"""
NOIR SOVEREIGN — DESKTOP SHORTCUT CREATOR
==========================================
Membuat shortcut 'Noir Sovereign.exe' di Desktop Windows.
Jalankan sekali saja: python create_desktop_shortcut.py
"""
import os, sys, shutil
from pathlib import Path

def create_shortcut():
    desktop = Path.home() / "Desktop"
    exe_src  = Path(__file__).parent / "dist" / "Noir Sovereign.exe"

    if not exe_src.exists():
        print(f"[ERROR] EXE tidak ditemukan di: {exe_src}")
        print("  Jalankan build dulu: pyinstaller --onefile --windowed --name 'Noir Sovereign' pc_launcher.py")
        sys.exit(1)

    # Coba buat shortcut via win32com
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(desktop / "Noir Sovereign.lnk"))
        shortcut.TargetPath     = str(exe_src)
        shortcut.WorkingDirectory = str(exe_src.parent)
        shortcut.Description    = "Noir Sovereign — AI Agent Dashboard"
        shortcut.WindowStyle    = 1  # Normal window
        shortcut.save()
        print(f"[OK] Shortcut dibuat di Desktop: {desktop / 'Noir Sovereign.lnk'}")
        return
    except Exception:
        pass

    # Fallback: Salin EXE langsung ke Desktop
    dst = desktop / "Noir Sovereign.exe"
    shutil.copy2(str(exe_src), str(dst))
    print(f"[OK] EXE disalin ke Desktop: {dst}")

if __name__ == "__main__":
    create_shortcut()
