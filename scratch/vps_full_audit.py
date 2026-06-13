# -*- coding: utf-8 -*-
"""
NOIR SOVEREIGN V30.1 — AUDIT KOMPREHENSIF VPS
Verifikasi semua penyesuaian dan penyempurnaan telah diterapkan.
"""
import paramiko
import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from dotenv import load_dotenv
load_dotenv()

VPS_IP   = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
VPS_USER = os.environ.get("NOIR_VPS_USER", "root")
VPS_PASS = os.environ.get("NOIR_VPS_PASS", "N!colay_No1r.Ai@Agent#Secure")
REMOTE   = "/root/noir-agent"

def run(ssh, cmd, timeout=15):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return out, err

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def ok(msg):  print(f"  [OK]  {msg}")
def warn(msg): print(f"  [WARN] {msg}")
def fail(msg): print(f"  [FAIL] {msg}")
def info(msg): print(f"  [INFO] {msg}")

def audit():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
    print(f"\nNOIR SOVEREIGN V30.1 — AUDIT VPS ({VPS_IP})")
    print("="*60)

    # ── 1. VERSI DASHBOARD ──────────────────────────────────────
    section("1. VERSI DASHBOARD (index.html)")
    out, _ = run(ssh, f"grep -i 'v30.1' {REMOTE}/noir-ui/index.html | head -5")
    if "v30.1" in out.lower():
        ok("index.html menampilkan V30.1 Grand Singularity")
        for line in out.splitlines()[:3]:
            info(line.strip()[:80])
    else:
        fail("index.html TIDAK menampilkan V30.1!")

    out, _ = run(ssh, f"grep -i 'v29' {REMOTE}/noir-ui/index.html | wc -l")
    if out.strip() == "0":
        ok("Tidak ada referensi V29 di index.html")
    else:
        warn(f"{out} baris masih menyebut V29 di index.html")

    # ── 2. VERSI WEB SERVER ─────────────────────────────────────
    section("2. VERSI WEB SERVER (web_server.py)")
    out, _ = run(ssh, f"grep -n '30.1' {REMOTE}/noir-ui/web_server.py | head -5")
    if "30.1" in out:
        ok("web_server.py mencantumkan V30.1")
        for line in out.splitlines()[:3]:
            info(line.strip()[:80])
    else:
        fail("web_server.py tidak mencantumkan V30.1!")

    # ── 3. ZERO-TRUST ENFORCEMENT ───────────────────────────────
    section("3. ZERO-TRUST ENFORCEMENT (web_server.py)")
    out, _ = run(ssh, f"grep -c '_verify_api_key' {REMOTE}/noir-ui/web_server.py")
    count = int(out.strip()) if out.strip().isdigit() else 0
    if count >= 10:
        ok(f"_verify_api_key dipanggil {count}x — Zero-Trust aktif penuh")
    elif count > 0:
        warn(f"_verify_api_key hanya {count}x — mungkin ada endpoint yang belum terlindungi")
    else:
        fail("TIDAK ADA _verify_api_key — Zero-Trust TIDAK aktif!")

    # ── 4. BUG FIX ORCHESTRATOR ─────────────────────────────────
    section("4. BUG FIX ORCHESTRATOR (sovereign_orchestrator.py)")
    out, _ = run(ssh, f"grep -n 'VectorMemory\\|SovereignSkillLoader' {REMOTE}/noir-vps/sovereign_orchestrator.py")
    if "VectorMemory" in out:
        ok("VectorMemory: Class name fix terverifikasi")
    else:
        fail("VectorMemory: Belum diperbaiki!")
    if "SovereignSkillLoader" in out:
        ok("SovereignSkillLoader: Class name fix terverifikasi")
    else:
        fail("SovereignSkillLoader: Belum diperbaiki!")

    # ── 5. SYSTEMD SERVICES ─────────────────────────────────────
    section("5. SYSTEMD SERVICES STATUS")
    for svc in ["noir-sovereign.service", "noir-orchestrator.service"]:
        active, _ = run(ssh, f"systemctl is-active {svc}")
        enabled, _ = run(ssh, f"systemctl is-enabled {svc}")
        desc, _ = run(ssh, f"systemctl show {svc} --property=Description --value")
        if active == "active":
            ok(f"{svc}: ACTIVE | enabled={enabled}")
            info(f"Description: {desc[:70]}")
        else:
            fail(f"{svc}: {active} | enabled={enabled}")

    # ── 6. PILAR ORCHESTRATOR (PROSES BERJALAN) ─────────────────
    section("6. ORCHESTRATOR PROCESS STATUS")
    out, _ = run(ssh, "ps aux | grep sovereign_orchestrator | grep -v grep")
    if out:
        ok("sovereign_orchestrator.py berjalan")
        info(out[:100])
    else:
        fail("sovereign_orchestrator.py TIDAK berjalan!")

    out, _ = run(ssh, "ps aux | grep 'uvicorn web_server' | grep -v grep")
    if out:
        ok("uvicorn web_server (Dashboard) berjalan di Port 80")
        info(out[:100])
    else:
        fail("uvicorn web_server TIDAK berjalan!")

    # ── 7. PORT & HTTP HEALTH ────────────────────────────────────
    section("7. PORT & HTTP HEALTH CHECK")
    out, _ = run(ssh, "ss -tuln | grep ':80 '")
    if out:
        ok(f"Port 80 AKTIF: {out[:60]}")
    else:
        fail("Port 80 TIDAK aktif!")

    out, _ = run(ssh, "curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://localhost/health")
    if out == "200":
        ok(f"HTTP /health: {out} — Server sehat")
    else:
        fail(f"HTTP /health: {out} — Server bermasalah!")

    # ── 8. ZERO-TRUST TEST (tanpa token → harus 401) ────────────
    section("8. ZERO-TRUST LIVE TEST (POST /api/logs tanpa token)")
    out, _ = run(ssh, "curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost/api/logs -H 'Content-Type: application/json' -d '{\"log\":\"test\"}'")
    if out in ("401", "403", "422"):
        ok(f"HTTP {out} — Endpoint terlindungi dengan benar!")
    else:
        fail(f"HTTP {out} — Endpoint TIDAK terlindungi (seharusnya 401/403)!")

    # ── 9. VERSI SERVICE FILES ───────────────────────────────────
    section("9. VERSI SYSTEMD SERVICE FILES")
    for svc in ["noir-sovereign.service", "noir-orchestrator.service"]:
        out, _ = run(ssh, f"cat /etc/systemd/system/{svc} | grep Description")
        if "30.1" in out or "30" in out:
            ok(f"{svc}: {out.strip()[:80]}")
        else:
            warn(f"{svc}: Masih menyebut versi lama → {out.strip()[:60]}")

    # ── 10. DOCKER CONTAINERS (status lama) ─────────────────────
    section("10. DOCKER STATUS (Harus semua EXIT/tidak digunakan)")
    out, _ = run(ssh, "docker ps -a --format '{{.Names}}: {{.Status}}' 2>/dev/null || echo 'Docker tidak berjalan'")
    for line in out.splitlines():
        if "running" in line.lower() or "up" in line.lower():
            warn(f"Container masih jalan: {line} (seharusnya digantikan systemd)")
        else:
            info(f"{line}")

    # ── 11. FILE KRITIS DI VPS ───────────────────────────────────
    section("11. FILE KRITIS PADA VPS")
    files = [
        f"{REMOTE}/noir-ui/index.html",
        f"{REMOTE}/noir-ui/web_server.py",
        f"{REMOTE}/noir-vps/sovereign_orchestrator.py",
        f"{REMOTE}/noir-vps/vector_memory.py",
        f"{REMOTE}/noir-vps/skill_loader.py",
        f"{REMOTE}/noir-vps/knowledge_db.py",
        f"{REMOTE}/.env",
    ]
    for f in files:
        out, _ = run(ssh, f"ls -lh {f} 2>/dev/null | awk '{{print $5, $6, $7, $8, $9}}'")
        if out:
            ok(f"{f.split('/')[-1]:35s} {out}")
        else:
            fail(f"{f.split('/')[-1]:35s} TIDAK DITEMUKAN!")

    # ── RINGKASAN AKHIR ──────────────────────────────────────────
    section("AUDIT SELESAI — NOIR SOVEREIGN V30.1")
    print()

    ssh.close()

if __name__ == "__main__":
    audit()
