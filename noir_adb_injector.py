"""
NOIR GHOST BRIDGE — ADB ANDROID INJECTOR
=========================================
Script injeksi otomatis ke Android via ADB.
Jalankan saat Redmi Note 14 terhubung via USB dengan USB Debugging aktif.
Tidak perlu build APK — langsung deploy Python service ke HP.

Cara pakai:
  1. Aktifkan USB Debugging di HP (Settings > Developer Options > USB Debugging)
  2. Colokkan HP ke PC via USB
  3. Jalankan: py noir_adb_injector.py
"""

import subprocess
import os
import sys
import time
import json
import shutil

DEVICE_ID     = "REDMI_NOTE14"
VPS_IP        = "8.215.23.17"
AUTH_TOKEN    = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
REMOTE_DIR    = "/data/local/tmp/noir"
SERVICE_SCRIPT= "noir_android_service.py"

# ── ANDROID SERVICE SCRIPT ─────────────────────────────────────────────────────
ANDROID_SERVICE_CODE = '''
import socket, json, time, os, threading, subprocess, urllib.request

VPS_IP    = "{vps_ip}"
AUTH      = "{auth}"
DEVICE_ID = "{device_id}"
INTERVAL  = 30  # detik

def ping_vps():
    """Kirim heartbeat ke VPS setiap INTERVAL detik."""
    while True:
        try:
            data = json.dumps({{
                "type":      "heartbeat",
                "device_id": DEVICE_ID,
                "platform":  "android",
                "ts":        time.time()
            }}).encode()
            req = urllib.request.Request(
                f"http://{{VPS_IP}}/api/node_ping",
                data=data,
                headers={{"Content-Type":"application/json",
                          "Authorization":f"Bearer {{AUTH}}"}}
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:
            pass
        time.sleep(INTERVAL)

def poll_commands():
    """Ambil perintah dari VPS dan eksekusi."""
    while True:
        try:
            req = urllib.request.Request(
                f"http://{{VPS_IP}}/api/node_commands?device_id={{DEVICE_ID}}",
                headers={{"Authorization":f"Bearer {{AUTH}}"}}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                cmds = json.loads(r.read())
            for cmd in cmds:
                if cmd.get("type") == "shell":
                    result = subprocess.run(
                        cmd["cmd"], shell=True,
                        capture_output=True, text=True, timeout=30
                    )
                    # Kirim hasil balik ke VPS
                    resp = json.dumps({{
                        "req_id":    cmd.get("req_id"),
                        "device_id": DEVICE_ID,
                        "stdout":    result.stdout[:2000],
                        "stderr":    result.stderr[:500],
                        "code":      result.returncode
                    }}).encode()
                    urllib.request.urlopen(urllib.request.Request(
                        f"http://{{VPS_IP}}/api/node_result",
                        data=resp,
                        headers={{"Content-Type":"application/json",
                                  "Authorization":f"Bearer {{AUTH}}"}}
                    ), timeout=10)
        except Exception:
            pass
        time.sleep(15)

if __name__ == "__main__":
    print(f"[NOIR ANDROID] Ghost Bridge aktif. Device: {{DEVICE_ID}}")
    t1 = threading.Thread(target=ping_vps,     daemon=True)
    t2 = threading.Thread(target=poll_commands, daemon=True)
    t1.start(); t2.start()
    # Jaga proses tetap hidup
    while True:
        time.sleep(60)
'''.format(vps_ip=VPS_IP, auth=AUTH_TOKEN, device_id=DEVICE_ID)


def run_adb(args, check=False):
    """Jalankan perintah adb."""
    cmd = ["adb"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result


def banner(text, color="\033[96m"):
    print(f"\n{color}{'='*54}\033[0m")
    print(f"{color}  {text}\033[0m")
    print(f"{color}{'='*54}\033[0m")


def check_adb():
    r = run_adb(["version"])
    if r.returncode != 0:
        print("\033[91m[ERROR] ADB tidak ditemukan di PATH!\033[0m")
        print("  Instal Android SDK Platform Tools dulu:")
        print("  https://developer.android.com/tools/releases/platform-tools")
        sys.exit(1)
    print(f"\033[92m[OK] ADB tersedia.\033[0m")


def wait_for_device():
    banner("MENUNGGU PERANGKAT ANDROID...", "\033[93m")
    print("  Pastikan USB Debugging AKTIF di HP Anda.")
    print("  Jika ada dialog 'Allow USB Debugging?' di HP → pilih ALLOW.")
    r = run_adb(["wait-for-device"])
    print("\033[92m[OK] Perangkat terdeteksi!\033[0m")


def get_device_info():
    banner("INFORMASI PERANGKAT", "\033[96m")
    props = {
        "Model"      : ["shell", "getprop", "ro.product.model"],
        "Android Ver": ["shell", "getprop", "ro.build.version.release"],
        "Serial"     : ["get-serialno"],
        "Architecture": ["shell", "getprop", "ro.product.cpu.abi"],
    }
    for label, args in props.items():
        r = run_adb(args)
        val = r.stdout.strip() or r.stderr.strip() or "—"
        print(f"  {label:<16}: \033[93m{val}\033[0m")


def deploy_service():
    banner("MENDEPLOY GHOST BRIDGE SERVICE", "\033[95m")

    # 1. Tulis service script ke temp lokal
    local_script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "_noir_android_tmp.py")
    with open(local_script, "w", encoding="utf-8") as f:
        f.write(ANDROID_SERVICE_CODE)
    print(f"  [1/4] Script service disiapkan: {local_script}")

    # 2. Buat direktori di HP
    r = run_adb(["shell", f"mkdir -p {REMOTE_DIR}"])
    print(f"  [2/4] Direktori '{REMOTE_DIR}' dibuat di HP")

    # 3. Push script ke HP
    remote_path = f"{REMOTE_DIR}/{SERVICE_SCRIPT}"
    r = run_adb(["push", local_script, remote_path])
    if r.returncode != 0:
        print(f"\033[91m  [ERROR] Gagal push: {r.stderr}\033[0m")
        return False
    print(f"  [3/4] Script berhasil di-push ke: {remote_path}")

    # 4. Jalankan service di background
    run_cmd = f"nohup python3 {remote_path} > {REMOTE_DIR}/noir.log 2>&1 &"
    r = run_adb(["shell", run_cmd])
    print(f"  [4/4] Service dijalankan di background HP")

    # Bersihkan temp
    try:
        os.unlink(local_script)
    except:
        pass

    return True


def verify_service():
    banner("VERIFIKASI SERVICE", "\033[92m")
    time.sleep(3)
    # Cek apakah proses berjalan
    r = run_adb(["shell", f"cat {REMOTE_DIR}/noir.log"])
    if "[NOIR ANDROID]" in r.stdout:
        print(f"\033[92m[✔] Ghost Bridge AKTIF di HP!\033[0m")
        print(f"    Log: {r.stdout.strip()[:200]}")
    else:
        print(f"\033[93m[?] Service mungkin berjalan (python3 tidak tersedia di ROM default).\033[0m")
        print(f"    Log output: {r.stdout[:200] or r.stderr[:200] or '(kosong)'}")

    # Cek PID
    r2 = run_adb(["shell", f"pgrep -f {SERVICE_SCRIPT}"])
    pid = r2.stdout.strip()
    if pid:
        print(f"\033[92m[✔] PID ditemukan: {pid}\033[0m")
    else:
        print(f"\033[93m[!] PID tidak ditemukan — python3 mungkin tidak tersedia di ROM ini.\033[0m")
        print(f"    Akan mencoba Termux fallback...")
        termux_fallback()


def termux_fallback():
    """Jika python3 tidak ada di shell HP, coba via Termux."""
    banner("TERMUX FALLBACK", "\033[93m")
    # Cek apakah Termux ada
    r = run_adb(["shell", "pm list packages | grep termux"])
    if "termux" in r.stdout:
        print(f"\033[92m[✔] Termux terdeteksi! Menjalankan via Termux...\033[0m")
        termux_cmd = (
            f"am start -n com.termux/.HomeActivity && "
            f"sleep 2 && "
            f"input text 'python3 {REMOTE_DIR}/{SERVICE_SCRIPT} &' && "
            f"input keyevent 66"
        )
        run_adb(["shell", termux_cmd])
    else:
        print(f"\033[91m[!] Termux tidak ditemukan.\033[0m")
        print(f"    Install Termux dari F-Droid, lalu jalankan kembali script ini.")
        print(f"    Atau install Termux APK dengan: adb install termux.apk")


def main():
    banner("NOIR GHOST BRIDGE — ANDROID INJECTOR", "\033[95m")
    print(f"  Target VPS : {VPS_IP}")
    print(f"  Device ID  : {DEVICE_ID}")

    check_adb()
    wait_for_device()
    get_device_info()
    success = deploy_service()
    if success:
        verify_service()

    banner("INJEKSI SELESAI", "\033[92m")
    print("  HP Anda sekarang terhubung ke Brain Noir VPS.")
    print("  Heartbeat dikirim setiap 30 detik secara otomatis.")
    print("  Anda bisa mencabut USB — service tetap berjalan di background.\n")


if __name__ == "__main__":
    main()
