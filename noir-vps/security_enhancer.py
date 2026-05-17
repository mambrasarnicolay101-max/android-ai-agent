"""
SOVEREIGN SECURITY ENHANCER v1.0 — NOIR SOVEREIGN
===================================================
Modul Pendukung: Audit Keamanan Lingkungan Otonom.

Fungsi:
  1. Audit environment variables untuk credential exposure
  2. Verifikasi permission file sensitif (.env)
  3. Hash integrity check pada file-file kritis sistem
  4. Scan untuk pola kode berbahaya dalam skill plugins
  5. Laporan audit lengkap ke Evolution Engine
"""
import os, logging, hashlib, json, time, stat

log = logging.getLogger("SecurityEnhancer")

CRITICAL_FILES = [
    "ai_router.py",
    "evolution_engine.py",
    "sovereign_orchestrator.py",
    "brain.py",
    "vector_memory.py",
    "sovereign_defense.py"
]

HASH_STORE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "integrity_hashes.json")

class SovereignSecurityEnhancer:
    """
    Melakukan audit keamanan menyeluruh terhadap lingkungan sistem.
    Dipanggil oleh SovereignMaintenance.run_full_audit() pada brain.py.
    """

    @staticmethod
    def _compute_hash(filepath: str) -> str:
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return f"ERROR:{e}"

    @staticmethod
    def audit_environment() -> dict:
        """Audit penuh: ENV, permissions, hash integrity, dan plugin scan."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "env_issues": [],
            "permission_issues": [],
            "integrity_violations": [],
            "plugin_warnings": [],
            "score": 100
        }

        # ── 1. ENV CREDENTIAL AUDIT ─────────────────────────────────────────
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            # Check .env is not world-readable
            mode = oct(os.stat(env_path).st_mode)[-3:]
            if mode[2] != "0":  # Others can read
                report["env_issues"].append(f".env file permissions too open: {mode}")
                report["score"] -= 10
                log.warning(f"[SECURITY] .env has permissive mode: {mode}")

            # Scan for placeholder/default credentials
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                env_content = f.read()
            if "YOUR_KEY_HERE" in env_content or "CHANGEME" in env_content:
                report["env_issues"].append("Placeholder credentials detected in .env")
                report["score"] -= 15

            log.info("[SECURITY] ENV audit complete.")
        else:
            report["env_issues"].append(".env file not found — system running without environment config")
            report["score"] -= 5

        # ── 2. FILE PERMISSION AUDIT ─────────────────────────────────────────
        sensitive_files = [env_path]
        for sf in sensitive_files:
            if os.path.exists(sf):
                try:
                    s = os.stat(sf)
                    if s.st_mode & stat.S_IWOTH:
                        report["permission_issues"].append(f"{sf} is world-writable!")
                        report["score"] -= 10
                except Exception as e:
                    report["permission_issues"].append(f"Cannot stat {sf}: {e}")

        # ── 3. INTEGRITY HASH CHECK ───────────────────────────────────────────
        base_dir = os.path.dirname(__file__)
        stored_hashes = {}
        if os.path.exists(HASH_STORE):
            try:
                with open(HASH_STORE, "r") as f:
                    stored_hashes = json.load(f)
            except: pass

        current_hashes = {}
        for fname in CRITICAL_FILES:
            fpath = os.path.join(base_dir, fname)
            if os.path.exists(fpath):
                current_hash = SovereignSecurityEnhancer._compute_hash(fpath)
                current_hashes[fname] = current_hash

                if fname in stored_hashes and stored_hashes[fname] != current_hash:
                    report["integrity_violations"].append(
                        f"INTEGRITY CHANGE: {fname} hash mismatch — file was modified"
                    )
                    log.warning(f"[SECURITY] Integrity change detected: {fname}")
                    report["score"] -= 5

        # Save new hashes as baseline
        os.makedirs(os.path.dirname(HASH_STORE), exist_ok=True)
        with open(HASH_STORE, "w") as f:
            json.dump(current_hashes, f, indent=4)

        # ── 4. PLUGIN SCAN ────────────────────────────────────────────────────
        skills_dir = os.path.join(base_dir, "skills")
        if os.path.exists(skills_dir):
            dangerous_patterns = ["os.system", "subprocess.call", "eval(", "exec(", "__import__"]
            for skill_file in os.listdir(skills_dir):
                if skill_file.endswith(".py"):
                    sfpath = os.path.join(skills_dir, skill_file)
                    try:
                        with open(sfpath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        for pat in dangerous_patterns:
                            if pat in content:
                                report["plugin_warnings"].append(
                                    f"Plugin {skill_file} contains pattern: '{pat}'"
                                )
                                report["score"] -= 2
                    except: pass

        report["score"] = max(0, report["score"])
        total_issues = len(report["env_issues"]) + len(report["permission_issues"]) + \
                       len(report["integrity_violations"]) + len(report["plugin_warnings"])

        log.info(f"[SECURITY] Audit selesai. Skor: {report['score']}/100 | Total Issues: {total_issues}")

        # Propose critical issues to evolution engine
        if report["score"] < 80:
            try:
                from evolution_engine import evolution_engine
                evolution_engine.propose_evolution(
                    title=f"[SECURITY] Audit Alert — Skor: {report['score']}/100",
                    description=f"Security audit menemukan {total_issues} masalah. Issues: " +
                               json.dumps(report["env_issues"] + report["integrity_violations"]),
                    changes={"security_audit": report},
                    complexity=6
                )
            except Exception as e:
                log.error(f"[SECURITY] Gagal melaporkan ke Evolution Engine: {e}")

        return report
