#!/usr/bin/env python3
"""
NOIR SCREEN CONTROLLER v1.0 — AUTONOMOUS PC DESKTOP CONTROL
============================================================
Memberikan AI agent kemampuan untuk melihat dan mengendalikan 
layar PC secara visual, mirip kemampuan Antigravity.

Kapabilitas:
- Screenshot layar utama / region tertentu
- Klik mouse, double-click, klik kanan
- Mengetik teks ke aplikasi aktif
- Scroll, drag & drop
- Membuka aplikasi / file
- OCR — membaca teks yang ada di layar
- Mencari elemen visual di layar (find_image)
"""
import os
import time
import logging
import threading
import base64
import json
from datetime import datetime
from pathlib import Path

log = logging.getLogger("ScreenController")

# ── Deteksi dependensi opsional ─────────────────────────────────────────────
try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Gerak mouse ke pojok kiri atas = emergency stop
    pyautogui.PAUSE = 0.05
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    log.warning("[SCREEN] pyautogui tidak tersedia. Install: pip install pyautogui")

try:
    from PIL import Image, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    log.warning("[SCREEN] Pillow tidak tersedia. Install: pip install Pillow")

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Path penyimpanan screenshot
SCREEN_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "screenshots"
SCREEN_DIR.mkdir(parents=True, exist_ok=True)

_action_log = []
_lock = threading.Lock()

def _log_action(action: str, result: dict):
    with _lock:
        entry = {"ts": datetime.now().isoformat(), "action": action, **result}
        _action_log.append(entry)
        if len(_action_log) > 200:
            _action_log[:] = _action_log[-200:]
        log.info(f"[SCREEN] {action} → {'OK' if result.get('success') else 'FAIL'}: {result.get('message','')}")


class NoirScreenController:
    """
    Pengendali Layar Otonom — AI dapat melihat dan berinteraksi
    dengan antarmuka grafis PC secara mandiri.
    """

    # ── VISION ─────────────────────────────────────────────────────────────────
    @staticmethod
    def screenshot(region=None, save: bool = True) -> dict:
        """
        Ambil screenshot. region=(x,y,w,h) untuk area tertentu, None untuk fullscreen.
        Returns: {success, path, base64, width, height}
        """
        if not HAS_PIL:
            return {"success": False, "message": "Pillow tidak terinstal."}
        try:
            if region:
                x, y, w, h = region
                img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            else:
                img = ImageGrab.grab()
            
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = SCREEN_DIR / f"screen_{ts}.png"
            
            if save:
                img.save(str(path))
            
            # Encode ke base64 untuk dikirim ke dashboard
            import io
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            
            result = {
                "success": True,
                "path": str(path),
                "base64": b64[:500] + "...",  # Potong untuk log, full dikirim via API
                "base64_full": b64,
                "width": img.width,
                "height": img.height,
                "message": f"Screenshot {img.width}x{img.height} berhasil."
            }
            _log_action("screenshot", result)
            return result
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("screenshot", r)
            return r

    @staticmethod
    def read_screen_text(region=None) -> dict:
        """OCR: Baca semua teks yang tampil di layar."""
        if not HAS_OCR:
            return {"success": False, "message": "pytesseract tidak terinstal. pip install pytesseract"}
        try:
            ss = NoirScreenController.screenshot(region=region, save=False)
            if not ss["success"]:
                return ss
            # Decode dari base64
            import io
            img_data = base64.b64decode(ss["base64_full"])
            img = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(img, lang="ind+eng")
            r = {"success": True, "text": text.strip(), "message": f"{len(text)} karakter terbaca."}
            _log_action("ocr_read_screen", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("ocr_read_screen", r)
            return r

    # ── MOUSE CONTROL ─────────────────────────────────────────────────────────
    @staticmethod
    def click(x: int, y: int, button: str = "left", clicks: int = 1) -> dict:
        """Klik mouse di koordinat (x, y)."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak terinstal."}
        try:
            pyautogui.click(x, y, button=button, clicks=clicks, interval=0.05)
            r = {"success": True, "message": f"Klik {button} di ({x},{y}) x{clicks}"}
            _log_action("click", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("click", r)
            return r

    @staticmethod
    def double_click(x: int, y: int) -> dict:
        """Double-click di koordinat (x, y)."""
        return NoirScreenController.click(x, y, clicks=2)

    @staticmethod
    def right_click(x: int, y: int) -> dict:
        """Klik kanan di koordinat (x, y)."""
        return NoirScreenController.click(x, y, button="right")

    @staticmethod
    def move_to(x: int, y: int, duration: float = 0.2) -> dict:
        """Gerakkan kursor mouse ke (x, y) dengan animasi."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak terinstal."}
        try:
            pyautogui.moveTo(x, y, duration=duration)
            r = {"success": True, "message": f"Kursor bergerak ke ({x},{y})"}
            _log_action("move_to", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("move_to", r)
            return r

    @staticmethod
    def scroll(x: int, y: int, amount: int = 3, direction: str = "up") -> dict:
        """Scroll di posisi (x, y). direction: 'up' atau 'down'."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak terinstal."}
        try:
            pyautogui.moveTo(x, y)
            clicks = amount if direction == "up" else -amount
            pyautogui.scroll(clicks)
            r = {"success": True, "message": f"Scroll {direction} {amount}x di ({x},{y})"}
            _log_action("scroll", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("scroll", r)
            return r

    @staticmethod
    def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> dict:
        """Drag dari (x1,y1) ke (x2,y2)."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak terinstal."}
        try:
            pyautogui.moveTo(x1, y1)
            pyautogui.dragTo(x2, y2, duration=duration, button="left")
            r = {"success": True, "message": f"Drag ({x1},{y1}) → ({x2},{y2})"}
            _log_action("drag", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("drag", r)
            return r

    # ── KEYBOARD CONTROL ──────────────────────────────────────────────────────
    @staticmethod
    def type_text(text: str, interval: float = 0.03) -> dict:
        """Ketikkan teks ke aplikasi aktif saat ini."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak terinstal."}
        try:
            pyautogui.typewrite(text, interval=interval)
            r = {"success": True, "message": f"Mengetik {len(text)} karakter."}
            _log_action("type_text", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("type_text", r)
            return r

    @staticmethod
    def hotkey(*keys) -> dict:
        """Tekan kombinasi tombol (misal: hotkey('ctrl','c') untuk copy)."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak terinstal."}
        try:
            pyautogui.hotkey(*keys)
            r = {"success": True, "message": f"Hotkey: {'+'.join(keys)}"}
            _log_action("hotkey", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("hotkey", r)
            return r

    @staticmethod
    def press_key(key: str) -> dict:
        """Tekan satu tombol keyboard (misal: 'enter', 'escape', 'f5')."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak terinstal."}
        try:
            pyautogui.press(key)
            r = {"success": True, "message": f"Tombol '{key}' ditekan."}
            _log_action("press_key", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("press_key", r)
            return r

    # ── APLIKASI CONTROL ──────────────────────────────────────────────────────
    @staticmethod
    def open_application(app_name: str) -> dict:
        """Buka aplikasi di Windows (misal: 'notepad', 'calc', 'chrome')."""
        import subprocess
        try:
            subprocess.Popen(app_name, shell=True)
            time.sleep(1)
            r = {"success": True, "message": f"Aplikasi '{app_name}' dibuka."}
            _log_action("open_application", r)
            return r
        except Exception as e:
            r = {"success": False, "message": str(e)}
            _log_action("open_application", r)
            return r

    @staticmethod
    def get_screen_size() -> dict:
        """Dapatkan ukuran resolusi layar saat ini."""
        if not HAS_PYAUTOGUI:
            if HAS_PIL:
                img = ImageGrab.grab()
                return {"success": True, "width": img.width, "height": img.height}
            return {"success": False, "message": "Tidak dapat mendeteksi ukuran layar."}
        try:
            w, h = pyautogui.size()
            return {"success": True, "width": w, "height": h,
                    "message": f"Resolusi layar: {w}x{h}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_mouse_position() -> dict:
        """Dapatkan posisi kursor mouse saat ini."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "message": "pyautogui tidak tersedia."}
        pos = pyautogui.position()
        return {"success": True, "x": pos.x, "y": pos.y}

    # ── LOG ───────────────────────────────────────────────────────────────────
    @staticmethod
    def get_action_log(limit: int = 20) -> list:
        with _lock:
            return _action_log[-limit:]


# ── Singleton Alias ───────────────────────────────────────────────────────────
screen = NoirScreenController

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== NoirScreenController Self-Test ===")
    
    sz = NoirScreenController.get_screen_size()
    print(f"[Screen Size] {sz}")
    
    pos = NoirScreenController.get_mouse_position()
    print(f"[Mouse Pos] {pos}")
    
    ss = NoirScreenController.screenshot(save=True)
    print(f"[Screenshot] Saved to: {ss.get('path')} ({ss.get('width')}x{ss.get('height')})")
    
    print("\nNoirScreenController Ready.")
