#!/usr/bin/env python3
"""
NOIR SOVEREIGN PC EXECUTOR v1.0 [AUTONOMOUS PC MODE]
====================================================
Sandbox eksekutor lokal yang memungkinkan AI Agent
menjalankan tugas-tugas mandiri di PC ASUS tanpa
bergantung pada koneksi Redmi Note 14.

Kapabilitas:
- Menjalankan kode Python dalam sandbox terisolasi
- Eksekusi perintah Shell dengan filter keamanan
- Penulisan dan pembacaan file pengetahuan (Knowledge Base)
- Pemantauan sumber daya PC secara real-time
"""

import os, sys, time, json, subprocess, io, contextlib, psutil, logging, threading, hashlib
from pathlib import Path
from datetime import datetime

log = logging.getLogger("PCExecutor")

# Path ke Knowledge Base di proyek
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
SANDBOX_DIR   = BASE_DIR / "noir-vps" / ".sandbox"
KNOWLEDGE_DIR.mkdir(exist_ok=True)
SANDBOX_DIR.mkdir(exist_ok=True)

# ─── GLOBAL SOVEREIGN STATE ─────────────────────────────────────────────────
# (Moved into PCExecutor class for consistency)

def toggle_override(state: bool):
    PCExecutor.SOVEREIGN_OVERRIDE = state
    log.info(f"Sovereign Override: {'ENABLED (UNRESTRICTED)' if state else 'DISABLED (PROTECTED)'}")

# ─── BLACKLIST PERINTAH BERBAHAYA ───────────────────────────────────────────
SHELL_BLACKLIST = [
    "rm -rf", "rmdir /s", "format c:", "del /f /s /q",
    "shutdown", "reboot", "> /dev/sda", "dd if=",
    ":(){ :|:& };:", "deltree", "reg delete", "bcdedit",
    "cipher /w", "sfc /scannow"  # hanya diblokir jika bukan admin
]

def _is_safe_shell(cmd: str) -> tuple[bool, str]:
    """Periksa keamanan perintah shell sebelum dieksekusi."""
    if PCExecutor.SOVEREIGN_OVERRIDE:
        return True, "Sovereign Override Active"
    lower = cmd.lower().strip()
    for blocked in SHELL_BLACKLIST:
        if blocked in lower:
            return False, f"Perintah diblokir oleh kebijakan keamanan: '{blocked}'"
    return True, "OK"

def _is_safe_code(code: str) -> tuple[bool, str]:
    """Periksa keamanan kode Python sebelum dieksekusi."""
    if PCExecutor.SOVEREIGN_OVERRIDE:
        return True, "Sovereign Override Active"
    dangerous = ["__import__('os').system", "shutil.rmtree", "os.remove", 
                 "open('/etc", "open('C:\\\\Windows", "subprocess.Popen"]
    for d in dangerous:
        if d in code:
            return False, f"Operasi berbahaya terdeteksi dalam kode: '{d}'"
    return True, "OK"

# ─── KELAS UTAMA PC EXECUTOR ─────────────────────────────────────────────────

class PCExecutor:
    """
    Engine eksekusi mandiri AI Agent di PC.
    Semua hasil eksekusi disimpan ke log dan Knowledge Base.
    """
    SOVEREIGN_OVERRIDE = False  # Jika TRUE, semua batasan keamanan dimatikan sementara
    _results_log = []
    _lock = threading.Lock()

    # ── 1. Eksekutor Shell (Dengan Filter Keamanan) ──────────────────────────
    @staticmethod
    def run_shell(cmd: str, timeout: int = 30) -> dict:
        """Jalankan perintah shell secara aman."""
        safe, reason = _is_safe_shell(cmd)
        if not safe:
            log.warning(f"Shell Blocked: {cmd}")
            return {"success": False, "output": f"[BLOCKED] {reason}", "cmd": cmd}

        log.info(f"PC Shell: {cmd}")
        try:
            proc = subprocess.run(
                cmd, shell=True, capture_output=True,
                text=True, timeout=timeout,
                cwd=str(BASE_DIR)
            )
            output = proc.stdout + proc.stderr
            result = {
                "success": proc.returncode == 0,
                "output": output[:4096],
                "returncode": proc.returncode,
                "cmd": cmd,
                "ts": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            result = {"success": False, "output": f"Timeout setelah {timeout}s", "cmd": cmd}
        except Exception as e:
            result = {"success": False, "output": str(e), "cmd": cmd}

        PCExecutor._log_result("shell", result)
        return result

    # ── 2. Eksekutor Python Sandbox ───────────────────────────────────────────
    @staticmethod
    def run_python(code: str, timeout: int = 30) -> dict:
        """Jalankan kode Python dalam sandbox terisolasi."""
        safe, reason = _is_safe_code(code)
        if not safe:
            return {"success": False, "output": f"[BLOCKED] {reason}", "code_hash": hashlib.md5(code.encode()).hexdigest()[:8]}

        log.info(f"PC Python Sandbox: Running {len(code)} chars of code...")
        
        stdout_capture = io.StringIO()
        sandbox_globals = {
            "__builtins__": {
                "print": print, "len": len, "range": range, "str": str,
                "int": int, "float": float, "list": list, "dict": dict,
                "tuple": tuple, "set": set, "bool": bool, "type": type,
                "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
                "sorted": sorted, "sum": sum, "min": min, "max": max,
                "abs": abs, "round": round, "format": format,
                "isinstance": isinstance, "hasattr": hasattr, "getattr": getattr,
            },
            "time": time, "json": json, "math": __import__("math"),
            "datetime": datetime, "Path": Path, "re": __import__("re"),
        }

        result = {}
        try:
            with contextlib.redirect_stdout(stdout_capture):
                exec(compile(code, "<sandbox>", "exec"), sandbox_globals)
            output = stdout_capture.getvalue()
            result = {
                "success": True,
                "output": output[:4096] if output else "(Kode berhasil dieksekusi tanpa output)",
                "ts": datetime.now().isoformat()
            }
        except Exception as e:
            result = {"success": False, "output": f"Error: {type(e).__name__}: {e}"}

        PCExecutor._log_result("python_sandbox", result)
        return result

    # ── 3. Penulis & Pembaca Knowledge Base ───────────────────────────────────
    @staticmethod
    def write_knowledge(key: str, data: any, category: str = "general") -> dict:
        """Simpan pengetahuan baru ke file JSON terstruktur."""
        try:
            kb_path = KNOWLEDGE_DIR / f"pc_knowledge_{category}.json"
            kb = {}
            if kb_path.exists():
                with open(kb_path, "r", encoding="utf-8") as f:
                    kb = json.load(f)

            kb[key] = {
                "data": data,
                "ts": datetime.now().isoformat(),
                "source": "PC_Autonomous_Learning"
            }

            with open(kb_path, "w", encoding="utf-8") as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)

            log.info(f"Knowledge Written: [{category}] {key}")
            return {"success": True, "key": key, "category": category, "path": str(kb_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def read_knowledge(key: str = None, category: str = "general") -> dict:
        """Baca pengetahuan dari Knowledge Base."""
        try:
            kb_path = KNOWLEDGE_DIR / f"pc_knowledge_{category}.json"
            if not kb_path.exists():
                return {"success": False, "error": "Knowledge base kosong."}
            with open(kb_path, "r", encoding="utf-8") as f:
                kb = json.load(f)
            if key:
                return {"success": True, "data": kb.get(key, {}).get("data")}
            return {"success": True, "keys": list(kb.keys()), "total": len(kb)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── 4. Pemantau Sumber Daya PC ────────────────────────────────────────────
    @staticmethod
    def get_system_stats() -> dict:
        """Ambil status hardware PC secara real-time."""
        try:
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(str(BASE_DIR.anchor))
            return {
                "success": True,
                "cpu_percent":   psutil.cpu_percent(interval=0.5),
                "ram_used_gb":   round(mem.used / 1e9, 2),
                "ram_total_gb":  round(mem.total / 1e9, 2),
                "ram_percent":   mem.percent,
                "disk_used_gb":  round(disk.used / 1e9, 2),
                "disk_total_gb": round(disk.total / 1e9, 2),
                "disk_percent":  disk.percent,
                "ts":            datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── 5. Logger Internal ────────────────────────────────────────────────────
    @staticmethod
    def _log_result(task_type: str, result: dict):
        with PCExecutor._lock:
            PCExecutor._results_log.append({
                "type": task_type, **result
            })
            # Batasi log di memori (200 entri terakhir)
            if len(PCExecutor._results_log) > 200:
                PCExecutor._results_log = PCExecutor._results_log[-200:]

    @staticmethod
    def get_logs(limit: int = 50) -> list:
        with PCExecutor._lock:
            return PCExecutor._results_log[-limit:]


# ─── SELF-TEST ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== PC Executor Self-Test ===")

    # Test 1: Stats
    stats = PCExecutor.get_system_stats()
    print(f"\n[System] CPU: {stats.get('cpu_percent')}% | RAM: {stats.get('ram_used_gb')}GB/{stats.get('ram_total_gb')}GB")

    # Test 2: Python Sandbox
    code = "x = [i**2 for i in range(10)]\nprint(f'Hasil: {x}')"
    res = PCExecutor.run_python(code)
    print(f"\n[Sandbox] {res.get('output')}")

    # Test 3: Knowledge Write/Read
    PCExecutor.write_knowledge("test_entry", {"info": "PC Executor OK", "version": "1.0"}, "test")
    read = PCExecutor.read_knowledge(category="test")
    print(f"\n[Knowledge] Keys: {read.get('keys')}")

    print("\nPC Executor Ready.")
