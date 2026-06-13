#!/usr/bin/env python3
"""
NOIR WINDOWS AUTO-BOOT SERVICE v1.0
=====================================
Mendaftarkan seluruh ekosistem Noir Sovereign sebagai Windows Task Scheduler
yang berjalan otomatis setiap kali PC menyala, tanpa perlu login manual.

Jalankan script ini SEKALI sebagai Administrator untuk instalasi permanen.
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

log = logging.getLogger("NoirServiceInstaller")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ── Konfigurasi Path ───────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
VPS_DIR     = BASE_DIR / "noir-vps"
UI_DIR      = BASE_DIR / "noir-ui"
PYTHON_EXE  = sys.executable

# ── Daftar Task yang akan diregistrasikan ─────────────────────────────────────
NOIR_TASKS = [
    {
        "name":        "NoirSovereign_WebServer",
        "description": "Noir Sovereign Web API Server - selalu aktif di port 80",
        "script":      str(UI_DIR / "web_server.py"),
        "workdir":     str(UI_DIR),
        "delay":       "PT30S",   # Mulai 30 detik setelah login
    },
    {
        "name":        "NoirSovereign_SingularityDaemon",
        "description": "Noir Sovereign Grand Singularity AI Learning Daemon",
        "script":      str(VPS_DIR / "singularity_daemon.py"),
        "workdir":     str(VPS_DIR),
        "delay":       "PT90S",   # Mulai 90 detik setelah login (tunggu web server)
    },
    {
        "name":        "NoirSovereign_Watchdog",
        "description": "Noir Sovereign Self-Healing Watchdog Monitor",
        "script":      str(VPS_DIR / "watchdog.py"),
        "workdir":     str(VPS_DIR),
        "delay":       "PT120S",  # Mulai 2 menit setelah login
    },
]

def _run_schtasks(args: list) -> tuple[bool, str]:
    """Jalankan perintah schtasks.exe dan return (success, output)."""
    try:
        result = subprocess.run(
            ["schtasks"] + args,
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output.strip()
    except Exception as e:
        return False, str(e)

def install_task(task: dict) -> bool:
    """Daftarkan satu task ke Windows Task Scheduler."""
    name    = task["name"]
    cmd     = f'"{PYTHON_EXE}" "{task["script"]}"'
    workdir = task["workdir"]
    delay   = task["delay"]

    log.info(f"[INSTALLER] Mendaftarkan task: {name}")

    # Hapus task lama jika ada
    _run_schtasks(["/Delete", "/TN", name, "/F"])

    # Buat XML task definition
    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{task['description']}</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>{delay}</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <RestartOnFailure>
      <Interval>PT2M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{PYTHON_EXE}</Command>
      <Arguments>"{task['script']}"</Arguments>
      <WorkingDirectory>{workdir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    # Simpan XML sementara
    xml_path = BASE_DIR / f"_task_{name}.xml"
    try:
        with open(xml_path, "w", encoding="utf-16") as f:
            f.write(xml_content)

        success, output = _run_schtasks(["/Create", "/TN", name, "/XML", str(xml_path), "/F"])
        if success:
            log.info(f"[INSTALLER] ✔ Task '{name}' berhasil didaftarkan.")
        else:
            log.error(f"[INSTALLER] ✘ Gagal mendaftarkan '{name}': {output}")
        return success
    finally:
        if xml_path.exists():
            xml_path.unlink()

def uninstall_all():
    """Hapus semua task Noir dari Task Scheduler."""
    log.info("[INSTALLER] Menghapus semua task Noir Sovereign...")
    for task in NOIR_TASKS:
        ok, out = _run_schtasks(["/Delete", "/TN", task["name"], "/F"])
        status = "✔ Dihapus" if ok else f"✘ Gagal: {out}"
        log.info(f"[INSTALLER] {task['name']}: {status}")

def check_status():
    """Cek status semua task terdaftar."""
    log.info("[INSTALLER] Status Task Scheduler Noir Sovereign:")
    for task in NOIR_TASKS:
        ok, out = _run_schtasks(["/Query", "/TN", task["name"], "/FO", "LIST"])
        if ok:
            lines = [l for l in out.splitlines() if "Status" in l or "Next Run" in l]
            log.info(f"  {task['name']}: {' | '.join(lines)}")
        else:
            log.warning(f"  {task['name']}: TIDAK TERDAFTAR")

def install_all():
    """Instal semua task Noir Sovereign ke Windows Task Scheduler."""
    log.info("=" * 60)
    log.info("  NOIR SOVEREIGN — Windows Auto-Boot Service Installer")
    log.info("=" * 60)
    
    results = {}
    for task in NOIR_TASKS:
        results[task["name"]] = install_task(task)
    
    passed = sum(1 for v in results.values() if v)
    log.info(f"\n[INSTALLER] Instalasi selesai: {passed}/{len(NOIR_TASKS)} task berhasil.")
    
    if passed == len(NOIR_TASKS):
        log.info("[INSTALLER] ✔ SEMUA SISTEM NOIR AKAN AKTIF OTOMATIS SAAT PC MENYALA.")
    else:
        failed = [k for k, v in results.items() if not v]
        log.warning(f"[INSTALLER] Task yang gagal: {failed}")
        log.warning("[INSTALLER] Coba jalankan PowerShell sebagai Administrator.")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "uninstall":
            uninstall_all()
        elif cmd == "status":
            check_status()
        else:
            print("Usage: python noir_windows_service.py [install|uninstall|status]")
    else:
        install_all()
