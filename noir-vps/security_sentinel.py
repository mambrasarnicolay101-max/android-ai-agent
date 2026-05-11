"""
SECURITY SENTINEL v2.0 — NOIR SOVEREIGN
==========================================
Pilar 2: Static & Dynamic Security Analysis
- SAST: Scan kode untuk pola berbahaya
- Dependency audit: Cek versi library usang
- CVE feed: Ambil kerentanan terbaru dari NVD
- Usulkan perbaikan via Evolution Engine
"""
import os, re, json, logging, time
import urllib.request

log = logging.getLogger("SecuritySentinel")

# Pola berbahaya dalam kode (SAST rules)
SAST_RULES = [
    (r"eval\s*\(", "HIGH", "Penggunaan eval() berbahaya - risiko code injection"),
    (r"exec\s*\(", "HIGH", "Penggunaan exec() berbahaya - risiko code injection"),
    (r"os\.system\s*\(", "MEDIUM", "os.system() tanpa sanitasi - risiko command injection"),
    (r"subprocess.*shell\s*=\s*True", "HIGH", "subprocess dengan shell=True - risiko shell injection"),
    (r"pickle\.load", "HIGH", "Deserialisasi pickle tidak aman - risiko RCE"),
    (r"password\s*=\s*['\"][^'\"]+['\"]", "CRITICAL", "Hardcoded password terdeteksi"),
    (r"secret\s*=\s*['\"][^'\"]+['\"]", "CRITICAL", "Hardcoded secret terdeteksi"),
    (r"api_key\s*=\s*['\"][^'\"]+['\"]", "HIGH", "Hardcoded API key terdeteksi"),
    (r"SELECT.*\+.*WHERE", "HIGH", "Potensi SQL Injection - gunakan parameterized query"),
    (r"innerHTML\s*=", "MEDIUM", "innerHTML assignment - risiko XSS"),
    (r"md5\s*\(", "MEDIUM", "MD5 tidak aman untuk kriptografi"),
    (r"http://", "LOW", "HTTP tidak terenkripsi - gunakan HTTPS"),
    (r"DEBUG\s*=\s*True", "MEDIUM", "Debug mode aktif di production"),
    (r"ALLOWED_HOSTS\s*=\s*\[.*\*", "HIGH", "ALLOWED_HOSTS terlalu permisif"),
    (r"random\.(random|randint|choice)", "LOW", "random module tidak kriptografis aman - gunakan secrets"),
]

class SecuritySentinel:
    """
    Sistem SAST/DAST otomatis untuk audit keamanan kode.
    Berjalan secara mandiri dan mengusulkan perbaikan via Evolution Engine.
    """

    SCAN_DIRS = ["noir-vps", "noir-ui"]
    CVE_FEED_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5&keywordSearch=python"
    _last_cve_fetch = 0
    _cve_cache = []

    @staticmethod
    def scan_file(filepath: str) -> list:
        """Scan satu file untuk pola SAST."""
        findings = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                lines = content.split("\n")

            for pattern, severity, message in SAST_RULES:
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        # FIX M-02: Abaikan peringatan `random` untuk file internal
                        if "random" in pattern and any(w in filepath for w in ["local_brain.py", "ai_router.py", "neural_coder.py"]):
                            continue
                        
                        findings.append({
                            "file": filepath,
                            "line": i + 1,
                            "severity": severity,
                            "message": message,
                            "snippet": line.strip()[:80]
                        })
        except Exception as e:
            log.debug(f"Cannot scan {filepath}: {e}")
        return findings

    @staticmethod
    def scan_codebase() -> dict:
        """Scan seluruh codebase dan kembalikan laporan SAST."""
        log.info("[SENTINEL] Memulai scan SAST seluruh codebase...")
        all_findings = []
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        for scan_dir in SecuritySentinel.SCAN_DIRS:
            dir_path = os.path.join(base, scan_dir)
            if not os.path.exists(dir_path):
                continue
            for root, _, files in os.walk(dir_path):
                for fname in files:
                    if fname.endswith((".py", ".js", ".ts", ".html")):
                        fpath = os.path.join(root, fname)
                        findings = SecuritySentinel.scan_file(fpath)
                        all_findings.extend(findings)

        # Kelompokkan berdasarkan severity
        summary = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
        for f in all_findings:
            sev = f.get("severity", "LOW")
            if sev in summary:
                summary[sev].append(f)

        total = len(all_findings)
        log.info(f"[SENTINEL] Scan selesai: {total} temuan | CRITICAL:{len(summary['CRITICAL'])} HIGH:{len(summary['HIGH'])} MEDIUM:{len(summary['MEDIUM'])}")
        return summary

    @staticmethod
    def fetch_cve_feed() -> list:
        """Ambil CVE terbaru dari NVD untuk Python-related vulns."""
        now = time.time()
        # Cache 6 jam
        if now - SecuritySentinel._last_cve_fetch < 21600 and SecuritySentinel._cve_cache:
            return SecuritySentinel._cve_cache

        try:
            log.info("[SENTINEL] Mengambil feed CVE terbaru dari NVD...")
            req = urllib.request.Request(SecuritySentinel.CVE_FEED_URL,
                headers={"User-Agent": "NoirSovereign/21.2"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            cves = []
            for item in data.get("vulnerabilities", []):
                cve = item.get("cve", {})
                cves.append({
                    "id": cve.get("id"),
                    "description": cve.get("descriptions", [{}])[0].get("value", "")[:200],
                    "published": cve.get("published", "")[:10]
                })
            SecuritySentinel._cve_cache = cves
            SecuritySentinel._last_cve_fetch = now
            log.info(f"[SENTINEL] {len(cves)} CVE terbaru berhasil diambil.")
            return cves
        except Exception as e:
            log.warning(f"[SENTINEL] CVE fetch gagal: {e}")
            return []

    @staticmethod
    def propose_fixes(findings: dict):
        """Usulkan perbaikan untuk temuan kritis via Evolution Engine."""
        try:
            from evolution_engine import evolution_engine
        except ImportError:
            return

        critical = findings.get("CRITICAL", []) + findings.get("HIGH", [])
        if not critical:
            log.info("[SENTINEL] Tidak ada temuan kritis. Sistem aman.")
            return

        # Buat satu proposal per 3 temuan agar tidak spam
        for i in range(0, min(len(critical), 6), 3):
            batch = critical[i:i+3]
            desc_lines = [f"[{b['severity']}] {b['file']}:{b['line']} - {b['message']}" for b in batch]
            evolution_engine.propose_evolution(
                title=f"Security Hardening: {batch[0]['message'][:40]}",
                description="Security Sentinel mendeteksi kerentanan:\n" + "\n".join(desc_lines) +
                            "\n\nTindakan: Review dan perbaiki pola berbahaya ini.",
                changes={"security_fix": {"findings": batch}},
                complexity=3
            )
        log.info(f"[SENTINEL] {min(len(critical), 6)} security proposals dikirim ke Evolution Engine.")
    
    @staticmethod
    def heuristic_scan(filepath: str) -> bool:
        """
        [SHIELD v2.5] Analisis heuristik mendalam untuk mendeteksi malware/backdoor.
        Jika terdeteksi ancaman tinggi, file akan otomatis dikarantina.
        """
        log.info(f"[SHIELD] Memindai file mencurigakan: {os.path.basename(filepath)}")
        
        # Folder Karantina
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        quarantine_dir = os.path.join(base_dir, "noir-vps", ".sandbox", "quarantine")
        os.makedirs(quarantine_dir, exist_ok=True)

        findings = SecuritySentinel.scan_file(filepath)
        # Tambahan pola heuristik untuk backdoor
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                if ("atob(" in content or "base64.b64decode" in content) and ("eval(" in content or "exec(" in content):
                    findings.append({"severity": "CRITICAL", "message": "Potensi Obfuscated Backdoor terdeteksi"})
        except: pass

        high_risk = [f for f in findings if f['severity'] in ('CRITICAL', 'HIGH')]
        
        if high_risk:
            log.warning(f"[SHIELD] ANCAMAN TERDETEKSI: {filepath}")
            dest = os.path.join(quarantine_dir, os.path.basename(filepath) + f".{int(time.time())}.mal")
            try:
                import shutil
                shutil.copy2(filepath, dest)
                os.remove(filepath)
                log.info(f"[SHIELD] File telah DIKARANTINA: {dest}")
                
                # Alert ke Dashboard
                try:
                    GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "http://localhost:8765").rstrip("/")
                    API_KEY = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
                    HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
                    import requests
                    requests.post(f"{GATEWAY}/api/logs", headers=HEADERS, json={
                        "device_id": "SENTINEL_SHIELD",
                        "level": "CRITICAL",
                        "message": f"🚨 MALWARE SHIELD: File '{os.path.basename(filepath)}' dikarantina karena ancaman kritis."
                    }, timeout=5)
                except: pass
                return True
            except Exception as e:
                log.error(f"[SHIELD] Gagal mengarantina file: {e}")
        return False

    @staticmethod
    def run_full_audit():
        """Jalankan audit lengkap: SAST + CVE Feed + Heuristic Shield + Propose Fixes."""
        log.info("=" * 50)
        log.info("[SENTINEL] SOVEREIGN SECURITY AUDIT v2.5 DIMULAI")
        log.info("=" * 50)

        # Scan folder sensitif untuk heuristik (Skills & Sandbox)
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sensitive_dirs = [os.path.join(base, "noir-vps", "skills"), os.path.join(base, "noir-vps", ".sandbox")]
        for sdir in sensitive_dirs:
            if os.path.exists(sdir):
                for root, _, files in os.walk(sdir):
                    for f in files:
                        if f.endswith(".py"):
                            SecuritySentinel.heuristic_scan(os.path.join(root, f))

        findings = SecuritySentinel.scan_codebase()
        cves = SecuritySentinel.fetch_cve_feed()
        SecuritySentinel.propose_fixes(findings)

        # Simpan ke vector memory
        try:
            from vector_memory import vector_memory
            total = sum(len(v) for v in findings.values())
            vector_memory.add_experience(
                text=f"SECURITY AUDIT v2.5: {total} findings. Heuristic Shield active.",
                metadata={"source": "security_sentinel", "type": "audit_report"}
            )
        except Exception:
            pass

        log.info("[SENTINEL] AUDIT v2.5 SELESAI.")
        return findings


security_sentinel = SecuritySentinel()
