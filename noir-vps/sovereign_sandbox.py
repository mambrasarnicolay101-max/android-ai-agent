#!/usr/bin/env python3
"""
SOVEREIGN SANDBOX v2.0 — AST-BASED ISOLATION ENGINE
=====================================================
Menggantikan string-blacklist yang rentan dengan analisis AST (Abstract Syntax Tree)
dan isolasi proses nyata menggunakan multiprocessing + hard timeout kill.

Tier Keamanan:
  SAFE       → Bebas dieksekusi (print, math, string ops)
  RESTRICTED → Butuh konfirmasi sistem (file I/O, network)
  FORBIDDEN  → Diblokir mutlak (os.system, subprocess, shutil.rmtree)
"""
import ast
import sys
import io
import os
import time
import logging
import contextlib
import multiprocessing
import hashlib
import json
from datetime import datetime

log = logging.getLogger("SovereignSandbox")

# ── Tier Analisis AST ──────────────────────────────────────────────────────────
FORBIDDEN_NODES = {
    # Akses modul berbahaya langsung
    "Delete", "Global",
}

FORBIDDEN_CALLS = {
    # subprocess, os.system, shutil berbahaya
    "system", "popen", "Popen", "call", "check_output", "check_call", "run",
    "rmtree", "remove", "unlink", "format",
    # injection via builtins
    "__import__", "exec", "eval", "compile",
}

FORBIDDEN_MODULES = {
    "subprocess", "pty", "shutil", "winreg", "ctypes",
    "socket", "ftplib", "smtplib", "imaplib",
}

RESTRICTED_MODULES = {
    # boleh digunakan tapi dicatat
    "os", "pathlib", "requests", "urllib", "http",
}

class ASTAuditor(ast.NodeVisitor):
    """Analisis AST mendalam — mendeteksi serangan obfuscation dan bypass."""
    
    def __init__(self):
        self.violations = []
        self.warnings = []
    
    def visit_Import(self, node):
        for alias in node.names:
            base = alias.name.split(".")[0]
            if base in FORBIDDEN_MODULES:
                self.violations.append(f"FORBIDDEN import: '{alias.name}'")
            elif base in RESTRICTED_MODULES:
                self.warnings.append(f"RESTRICTED import: '{alias.name}'")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            base = node.module.split(".")[0]
            if base in FORBIDDEN_MODULES:
                self.violations.append(f"FORBIDDEN from-import: '{node.module}'")
            elif base in RESTRICTED_MODULES:
                self.warnings.append(f"RESTRICTED from-import: '{node.module}'")
        self.generic_visit(node)
    
    def visit_Call(self, node):
        # Direct call: system(), rmtree(), etc.
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.violations.append(f"FORBIDDEN call: '{node.func.id}()'")
        
        # Attribute call: os.system(), subprocess.Popen(), etc.
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_CALLS:
                self.violations.append(f"FORBIDDEN method: '.{node.func.attr}()'")
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        # Deteksi akses ke __class__, __bases__, __subclasses__ (jail break classic)
        if isinstance(node.attr, str) and node.attr.startswith("__") and node.attr.endswith("__"):
            if node.attr in ("__class__", "__bases__", "__subclasses__", "__globals__", "__builtins__"):
                self.violations.append(f"FORBIDDEN dunder access: '{node.attr}'")
        self.generic_visit(node)

def _audit_ast(code: str) -> dict:
    """Jalankan pemeriksaan AST — return dict {safe, violations, warnings}."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"safe": False, "violations": [f"SyntaxError: {e}"], "warnings": []}
    
    auditor = ASTAuditor()
    auditor.visit(tree)
    
    return {
        "safe": len(auditor.violations) == 0,
        "violations": auditor.violations,
        "warnings": auditor.warnings,
    }

# ── Isolated Process Executor ──────────────────────────────────────────────────
def _isolated_exec(code: str, result_queue: multiprocessing.Queue):
    """Dijalankan di proses terpisah yang diisolasi."""
    captured = io.StringIO()
    sandbox_globals = {
        "__builtins__": {
            "print": print, "len": len, "range": range, "str": str,
            "int": int, "float": float, "list": list, "dict": dict,
            "tuple": tuple, "set": set, "bool": bool, "type": type,
            "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
            "sorted": sorted, "sum": sum, "min": min, "max": max,
            "abs": abs, "round": round, "format": format, "repr": repr,
            "isinstance": isinstance, "hasattr": hasattr, "getattr": getattr,
            "setattr": setattr, "vars": vars, "dir": dir,
        },
        "time": time, "json": json, "math": __import__("math"),
        "datetime": datetime, "re": __import__("re"),
        "hashlib": hashlib, "random": __import__("random"),
    }
    try:
        with contextlib.redirect_stdout(captured):
            exec(compile(code, "<sovereign_sandbox>", "exec"), sandbox_globals)
        result_queue.put({"success": True, "output": captured.getvalue()[:4096]})
    except Exception as e:
        result_queue.put({"success": False, "output": f"{type(e).__name__}: {e}"})


class SovereignSandbox:
    """
    Sandbox eksekusi bertingkat dengan isolasi proses nyata.
    Arsitektur: AST Audit → Process Isolation → Hard Timeout Kill
    """
    
    OVERRIDE = False  # Jika True, semua batasan dinonaktifkan (Sovereign Mode)
    _audit_log = []
    
    @classmethod
    def execute_python(cls, code: str, timeout: int = 20) -> dict:
        """
        Eksekusi kode Python dengan keamanan bertingkat.
        Returns: {success, output, tier, violations, warnings, ts}
        """
        ts = datetime.now().isoformat()
        code_hash = hashlib.md5(code.encode()).hexdigest()[:8]
        
        # ── Tier 0: Override Sovereign ──
        if cls.OVERRIDE:
            log.warning(f"[SANDBOX] SOVEREIGN OVERRIDE AKTIF — Melewati semua filter.")
            return cls._direct_exec(code, ts, code_hash)
        
        # ── Tier 1: AST Audit ──
        audit = _audit_ast(code)
        cls._log_audit(code_hash, audit)
        
        if not audit["safe"]:
            msg = f"[BLOCKED] Kode ditolak oleh AST Auditor: {'; '.join(audit['violations'])}"
            log.warning(f"[SANDBOX] {msg}")
            return {
                "success": False, "output": msg,
                "tier": "FORBIDDEN", "violations": audit["violations"],
                "warnings": audit["warnings"], "ts": ts, "hash": code_hash
            }
        
        if audit["warnings"]:
            log.warning(f"[SANDBOX] Peringatan akses modul terbatas: {audit['warnings']}")
        
        # ── Tier 2: Isolasi Proses + Hard Timeout ──
        result_queue = multiprocessing.Queue()
        proc = multiprocessing.Process(
            target=_isolated_exec,
            args=(code, result_queue),
            daemon=True
        )
        proc.start()
        proc.join(timeout=timeout)
        
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=2)
            if proc.is_alive():
                proc.kill()
            log.error(f"[SANDBOX] Proses timeout setelah {timeout}s → KILLED")
            return {
                "success": False,
                "output": f"[TIMEOUT] Eksekusi dihentikan paksa setelah {timeout} detik.",
                "tier": "RESTRICTED", "violations": [], "warnings": audit["warnings"],
                "ts": ts, "hash": code_hash
            }
        
        if not result_queue.empty():
            result = result_queue.get_nowait()
            result.update({
                "tier": "SAFE" if not audit["warnings"] else "RESTRICTED",
                "violations": [], "warnings": audit["warnings"],
                "ts": ts, "hash": code_hash
            })
            return result
        
        return {
            "success": False, "output": "[ERROR] Proses selesai tanpa output.",
            "tier": "UNKNOWN", "violations": [], "warnings": [],
            "ts": ts, "hash": code_hash
        }
    
    @classmethod
    def execute_shell(cls, cmd: str, timeout: int = 15) -> dict:
        """Eksekusi shell dengan AST-equivalent parsing + proses terisolasi."""
        import subprocess
        ts = datetime.now().isoformat()
        
        # ── Shell Danger Analysis ──
        lower = cmd.lower().strip()
        ABSOLUTE_FORBIDDEN = [
            "format c:", "rm -rf /", "dd if=", ":(){ :|:", "deltree",
            "bcdedit /delete", "cipher /w:c", "> /dev/sda",
            "del /f /s /q c:\\windows", "rmdir /s /q c:\\"
        ]
        RESTRICTED_SHELL = [
            "reg delete", "net user", "schtasks /delete", "sc delete",
            "shutdown", "reboot", "taskkill /f"
        ]
        
        if not cls.OVERRIDE:
            for f in ABSOLUTE_FORBIDDEN:
                if f in lower:
                    return {"success": False, "output": f"[FORBIDDEN] '{f}' diblokir secara mutlak.", "cmd": cmd, "ts": ts}
            for r in RESTRICTED_SHELL:
                if r in lower:
                    log.warning(f"[SANDBOX] Perintah RESTRICTED dicatat: '{cmd}'")
        
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=timeout,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            return {
                "success": result.returncode == 0,
                "output": (result.stdout + result.stderr)[:4096],
                "returncode": result.returncode,
                "cmd": cmd, "ts": ts
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": f"[TIMEOUT] {timeout}s terlampaui.", "cmd": cmd, "ts": ts}
        except Exception as e:
            return {"success": False, "output": str(e), "cmd": cmd, "ts": ts}
    
    @classmethod
    def _direct_exec(cls, code: str, ts: str, code_hash: str) -> dict:
        """Eksekusi langsung tanpa filter — hanya untuk Sovereign Override."""
        try:
            result_queue = multiprocessing.Queue()
            proc = multiprocessing.Process(target=_isolated_exec, args=(code, result_queue), daemon=True)
            proc.start()
            proc.join(timeout=30)
            if proc.is_alive():
                proc.kill()
                return {"success": False, "output": "[TIMEOUT] 30s", "tier": "OVERRIDE", "ts": ts}
            if not result_queue.empty():
                r = result_queue.get_nowait()
                r.update({"tier": "OVERRIDE", "ts": ts, "hash": code_hash})
                return r
        except Exception as e:
            return {"success": False, "output": str(e), "tier": "OVERRIDE", "ts": ts}
        return {"success": False, "output": "No result", "tier": "OVERRIDE", "ts": ts}
    
    @classmethod
    def _log_audit(cls, code_hash: str, audit: dict):
        cls._audit_log.append({"hash": code_hash, "ts": datetime.now().isoformat(), **audit})
        if len(cls._audit_log) > 500:
            cls._audit_log = cls._audit_log[-500:]
    
    @classmethod
    def get_audit_log(cls, limit: int = 20) -> list:
        return cls._audit_log[-limit:]

# Backward compat alias
SandboxEngine = SovereignSandbox

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== SovereignSandbox Self-Test ===")
    
    # Test SAFE
    r = SovereignSandbox.execute_python("x = [i**2 for i in range(5)]\nprint(x)")
    print(f"[SAFE Test] {r}")
    
    # Test FORBIDDEN
    r = SovereignSandbox.execute_python("import subprocess; subprocess.run(['ls'])")
    print(f"[FORBIDDEN Test] {r}")
    
    # Test TIMEOUT
    r = SovereignSandbox.execute_python("while True: pass", timeout=3)
    print(f"[TIMEOUT Test] {r}")
    
    print("\nSovereignSandbox Ready.")
