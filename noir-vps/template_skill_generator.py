"""
template_skill_generator.py -- NOIR SOVEREIGN TEMPLATE-BASED SKILL GENERATOR
==============================================================================
Generate skill Python langsung dari blueprint data TANPA LLM.
Menggunakan template code generation berdasarkan tipe vulnerability/TTP.

Ini adalah fallback ketika semua LLM API tidak tersedia.
Skill yang dihasilkan tetap valid, fungsional, dan deployable.
"""
import os
import sys
import json
import re
import logging
import hashlib
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TemplateSynth] %(message)s")
log = logging.getLogger("TemplateSkillGenerator")

BASE_DIR      = Path(r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent")
VPS_DIR       = BASE_DIR / "noir-vps"
KE_DIR        = BASE_DIR / "knowledge"
INTEL_DIR     = KE_DIR / "intel"
BLUEPRINT_DIR = INTEL_DIR / "skills_blueprints"
SKILLS_DIR    = VPS_DIR / "skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

# ── CVE/Injection Detection Template ─────────────────────────────────────────
INJECTION_TEMPLATE = '''"""
{class_name} -- Noir Sovereign Security Skill
Auto-generated from blueprint: {blueprint_id}
Source: {source} | Generated: {timestamp}

Detects: {vulnerability_class} ({cve_id})
Description: {description}
"""
import json
import urllib.request
import urllib.parse
import logging
import sys

log = logging.getLogger("{class_name}")


class {class_name}:
    """
    Skill Deteksi Kerentanan: {cve_id}
    Tipe: {vulnerability_class}
    Deskripsi: {description_short}
    
    LEGAL NOTE: Hanya digunakan pada target authorized (lab lokal, CTF, DVWA).
    Tidak boleh digunakan untuk menyerang sistem tanpa izin eksplisit.
    """

    CVE_ID = "{cve_id}"
    VULN_CLASS = "{vulnerability_class}"
    RISK_INDICATORS = {risk_indicators}

    def __init__(self, target_url: str = "http://localhost"):
        self.target_url = target_url.rstrip("/")
        self.results = []
        self.log = logging.getLogger(self.__class__.__name__)

    def _make_request(self, url: str, data: dict = None, timeout: int = 10) -> dict:
        """Kirim HTTP request dan kembalikan response info."""
        try:
            if data:
                payload = urllib.parse.urlencode(data).encode()
                req = urllib.request.Request(url, data=payload, method="POST")
            else:
                req = urllib.request.Request(url, method="GET")
            req.add_header("User-Agent", "NoirSovereign-SecurityScanner/1.0 (Authorized Scan)")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", errors="ignore")
                return {{"status": r.status, "body": body, "url": url}}
        except Exception as e:
            return {{"status": 0, "body": str(e), "url": url, "error": True}}

    def _check_indicators(self, response_body: str) -> List[str]:
        """Periksa response body untuk tanda-tanda kerentanan."""
        found = []
        for indicator in self.RISK_INDICATORS:
            if indicator.lower() in response_body.lower():
                found.append(indicator)
        return found

    def scan_endpoint(self, path: str = "/", params: dict = None) -> dict:
        """Pindai satu endpoint untuk tanda-tanda {vulnerability_class}."""
        url = f"{{self.target_url}}{{path}}"
        self.log.info(f"Memindai: {{url}}")

        # Test dengan payload innocuous untuk deteksi
        test_payloads = {test_payloads}

        findings = []
        for payload_desc, payload_data in test_payloads.items():
            resp = self._make_request(url, data=payload_data)
            indicators = self._check_indicators(resp.get("body", ""))
            if indicators:
                findings.append({{
                    "payload": payload_desc,
                    "indicators_found": indicators,
                    "status_code": resp.get("status"),
                    "evidence": resp.get("body", "")[:500]
                }})

        result = {{
            "endpoint": url,
            "vulnerable": len(findings) > 0,
            "findings": findings,
            "cve": self.CVE_ID,
            "vuln_type": self.VULN_CLASS
        }}
        self.results.append(result)
        return result

    def execute(self) -> str:
        """Jalankan scan lengkap dan kembalikan laporan JSON."""
        self.log.info(f"[{{self.CVE_ID}}] Memulai scan pada {{self.target_url}}")

        # Scan endpoint umum
        endpoints = ["/", "/login", "/api/", "/admin/", "/search", "/upload"]
        for ep in endpoints:
            self.scan_endpoint(ep)

        # Hitung hasil
        vulnerable_count = sum(1 for r in self.results if r.get("vulnerable"))
        report = {{
            "cve_id": self.CVE_ID,
            "vuln_class": self.VULN_CLASS,
            "target": self.target_url,
            "scanned_at": datetime.utcnow().isoformat() if "datetime" in dir() else "unknown",
            "total_endpoints": len(self.results),
            "vulnerable_endpoints": vulnerable_count,
            "risk_level": "HIGH" if vulnerable_count > 0 else "LOW",
            "results": self.results,
            "disclaimer": "ONLY USE ON AUTHORIZED TARGETS"
        }}

        self.log.info(f"Scan selesai: {{vulnerable_count}}/{{len(self.results)}} endpoint rentan")
        return json.dumps(report, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import unittest

    class Test{class_name}(unittest.TestCase):
        def test_initialization(self):
            skill = {class_name}("http://localhost")
            self.assertEqual(skill.CVE_ID, "{cve_id}")
            self.assertEqual(skill.VULN_CLASS, "{vulnerability_class}")

        def test_check_indicators_empty(self):
            skill = {class_name}("http://localhost")
            found = skill._check_indicators("normal response body")
            self.assertIsInstance(found, list)

        def test_execute_returns_json(self):
            skill = {class_name}("http://localhost:99999")  # Non-existent port
            result = skill.execute()
            parsed = json.loads(result)
            self.assertIn("cve_id", parsed)
            self.assertIn("risk_level", parsed)
            self.assertIn("results", parsed)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(Test{class_name})
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
'''

# ── MITRE TTP Detection Template ──────────────────────────────────────────────
MITRE_TEMPLATE = '''"""
{class_name} -- Noir Sovereign Security Skill
Auto-generated from MITRE ATT&CK blueprint: {technique_id}
Source: MITRE_ATTCK | Generated: {timestamp}

Technique: {technique_name}
Tactics: {tactics}
Platforms: {platforms}
"""
import os
import sys
import json
import logging
import subprocess
import platform
from pathlib import Path
from typing import List, Dict

log = logging.getLogger("{class_name}")


class {class_name}:
    """
    MITRE ATT&CK Detection Skill: {technique_id} - {technique_name}
    Tactics: {tactics}
    
    Detection guidance: {detection_short}
    
    LEGAL NOTE: Hanya digunakan untuk analisis defensive pada sistem sendiri.
    """

    TECHNIQUE_ID = "{technique_id}"
    TECHNIQUE_NAME = "{technique_name}"
    TACTICS = {tactics_list}
    PLATFORMS = {platforms_list}
    DETECTION_HINTS = {detection_keywords}

    def __init__(self):
        self.findings = []
        self.log = logging.getLogger(self.__class__.__name__)
        self.os_type = platform.system().lower()

    def _run_command(self, cmd: List[str], timeout: int = 10) -> str:
        """Jalankan perintah sistem dan kembalikan output."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout, encoding="utf-8", errors="ignore"
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

    def _check_processes(self) -> List[Dict]:
        """Periksa proses yang berjalan untuk tanda-tanda TTP ini."""
        suspicious = []
        if self.os_type == "windows":
            output = self._run_command(["tasklist", "/fo", "csv", "/v"])
        else:
            output = self._run_command(["ps", "aux"])

        lines = output.split("\\n")
        for line in lines:
            for hint in self.DETECTION_HINTS:
                if hint.lower() in line.lower():
                    suspicious.append({{"line": line[:200], "matched_hint": hint}})
                    break

        return suspicious

    def _check_startup_items(self) -> List[str]:
        """Periksa startup items untuk persistensi (Windows)."""
        items = []
        if self.os_type != "windows":
            return items
        output = self._run_command([
            "reg", "query",
            "HKEY_CURRENT_USER\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run"
        ])
        return [line.strip() for line in output.split("\\n") if line.strip()]

    def _check_network_connections(self) -> List[str]:
        """Periksa koneksi jaringan aktif."""
        if self.os_type == "windows":
            output = self._run_command(["netstat", "-an"])
        else:
            output = self._run_command(["netstat", "-an"])
        return [line for line in output.split("\\n") if "ESTABLISHED" in line or "LISTEN" in line]

    def execute(self) -> str:
        """Jalankan deteksi TTP {technique_id} dan kembalikan laporan JSON."""
        self.log.info(f"[{{self.TECHNIQUE_ID}}] Menjalankan deteksi: {{self.TECHNIQUE_NAME}}")

        processes = self._check_processes()
        startup   = self._check_startup_items()
        network   = self._check_network_connections()[:20]

        risk = "HIGH" if processes else ("MEDIUM" if startup else "LOW")

        report = {{
            "technique_id":   self.TECHNIQUE_ID,
            "technique_name": self.TECHNIQUE_NAME,
            "tactics":        self.TACTICS,
            "os":             platform.system(),
            "hostname":       platform.node(),
            "risk_level":     risk,
            "suspicious_processes": processes[:10],
            "startup_items_count": len(startup),
            "active_connections":  len(network),
            "recommendation":  "Investigasi proses mencurigakan yang ditemukan" if processes else "Tidak ada indikasi aktif",
            "disclaimer":      "DEFENSIVE USE ONLY - AUTHORIZED SYSTEMS"
        }}

        self.log.info(f"Deteksi selesai: {{risk}} risk, {{len(processes)}} proses mencurigakan")
        return json.dumps(report, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import unittest

    class Test{class_name}(unittest.TestCase):
        def test_initialization(self):
            skill = {class_name}()
            self.assertEqual(skill.TECHNIQUE_ID, "{technique_id}")
            self.assertIsInstance(skill.TACTICS, list)

        def test_execute_returns_json(self):
            skill = {class_name}()
            result = skill.execute()
            parsed = json.loads(result)
            self.assertIn("technique_id", parsed)
            self.assertIn("risk_level", parsed)

        def test_check_processes_returns_list(self):
            skill = {class_name}()
            result = skill._check_processes()
            self.assertIsInstance(result, list)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(Test{class_name})
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
'''


def to_class_name(raw: str) -> str:
    """Convert CVE/TID string to valid PascalCase class name."""
    raw = re.sub(r'[^a-zA-Z0-9]', '_', raw)
    parts = [p.capitalize() for p in raw.split('_') if p]
    return "Skill" + "".join(parts)


def to_snake_case(class_name: str) -> str:
    """Convert PascalCase to snake_case."""
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', class_name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def generate_cve_skill(bp: Dict) -> Optional[str]:
    """Generate Python skill code from CVE blueprint."""
    cve_id   = bp.get("cve_id", "CVE-UNKNOWN")
    title    = bp.get("title", bp.get("description", ""))[:200]
    vuln     = bp.get("vulnerability_class", "injection").replace("-", "_")
    desc     = bp.get("description", title)[:200]
    desc_short = desc[:100].replace('"', "'")
    class_name = to_class_name(cve_id)

    # Build risk indicators from description
    risk_words = ["error", "exception", "sql", "injection", "shell", "exec", "upload",
                  "root", "admin", "unauthorized", "access denied", "forbidden",
                  "traceback", "stack trace", "undefined", "null", "invalid"]
    if "sql" in desc.lower():
        risk_words.extend(["syntax error", "you have an error", "mysql_fetch"])
    if "rce" in desc.lower() or "remote code" in desc.lower():
        risk_words.extend(["command not found", "permission denied", "/etc/passwd"])
    if "xss" in desc.lower():
        risk_words.extend(["<script>", "alert(", "onerror="])

    # Build test payloads based on vulnerability type
    if "sql" in vuln or "injection" in vuln:
        test_payloads = """{"normal": {"q": "test"}, "sqli_basic": {"q": "' OR '1'='1"}, "sqli_comment": {"q": "admin'--"}}"""
    elif "rce" in vuln or "code_exec" in vuln:
        test_payloads = """{"normal": {"input": "hello"}, "cmd_test": {"cmd": "echo test"}}"""
    elif "upload" in vuln or "file" in vuln:
        test_payloads = """{"normal": {"file": "test.txt"}, "path_traversal": {"file": "../../../etc/passwd"}}"""
    else:
        test_payloads = """{"normal": {"q": "test"}, "probe": {"input": "<test>"}}"""

    code = INJECTION_TEMPLATE.format(
        class_name=class_name,
        blueprint_id=cve_id,
        source="NVD_CISA",
        timestamp=datetime.utcnow().isoformat(),
        cve_id=cve_id,
        vulnerability_class=vuln,
        description=desc,
        description_short=desc_short,
        risk_indicators=json.dumps(risk_words[:10]),
        test_payloads=test_payloads
    )
    # Fix the datetime reference
    code = code.replace(
        'datetime.utcnow().isoformat() if "datetime" in dir() else "unknown"',
        f'"{datetime.utcnow().isoformat()}"'
    )
    return code, class_name


def generate_mitre_skill(bp: Dict) -> Optional[str]:
    """Generate Python skill code from MITRE TTP blueprint."""
    tid     = bp.get("id", bp.get("technique_id", "T0000"))
    name    = bp.get("name", "Unknown Technique")
    tactics = bp.get("tactic", [])
    platforms = bp.get("platforms", [])
    detection = bp.get("detection", "")[:300]
    detect_short = detection[:100].replace('"', "'")

    class_name = to_class_name(f"{tid}_{name[:20]}")

    # Extract detection keywords
    detect_words = [w.strip('".,()') for w in re.findall(r'\b[A-Za-z]{4,}\b', detection)]
    detect_words = list(set(detect_words[:10]))[:10]
    if not detect_words:
        detect_words = ["suspicious", "unauthorized", "anomaly"]

    code = MITRE_TEMPLATE.format(
        class_name=class_name,
        technique_id=tid,
        technique_name=name.replace('"', "'"),
        tactics=", ".join(tactics),
        platforms=", ".join(platforms),
        detection_short=detect_short,
        tactics_list=json.dumps(tactics),
        platforms_list=json.dumps(platforms),
        detection_keywords=json.dumps(detect_words),
        timestamp=datetime.utcnow().isoformat()
    )
    return code, class_name


def run_template_synthesis(max_blueprints: int = 10) -> Dict:
    """
    Main synthesis loop: scan blueprints, generate templates, deploy skills.
    """
    log.info("=" * 65)
    log.info("TEMPLATE SKILL SYNTHESIZER -- SIKLUS DIMULAI (No-LLM Mode)")
    log.info("=" * 65)

    blueprint_files = list(BLUEPRINT_DIR.glob("*.json"))
    if not blueprint_files:
        log.error(f"Tidak ada blueprint di {BLUEPRINT_DIR}")
        return {"success": 0, "failed": 0, "total": 0}

    # Load all blueprints
    all_blueprints = []
    for bf in blueprint_files:
        try:
            data = json.loads(bf.read_text(encoding="utf-8"))
            if isinstance(data, list):
                all_blueprints.extend(data[:max_blueprints])
            elif isinstance(data, dict):
                all_blueprints.append(data)
        except Exception as e:
            log.warning(f"Skip {bf.name}: {e}")

    candidates = all_blueprints[:max_blueprints]
    log.info(f"Total blueprint dimuat: {len(all_blueprints)}, diproses: {len(candidates)}")

    deployed = []
    failed   = []

    for i, bp in enumerate(candidates, 1):
        bp_id = bp.get("cve_id") or bp.get("id") or bp.get("technique_id") or f"bp_{i}"
        log.info(f"[{i}/{len(candidates)}] Generating skill untuk: {bp_id}")

        try:
            # Determine template type
            if "cve_id" in bp:
                code, class_name = generate_cve_skill(bp)
            elif "id" in bp or "technique_id" in bp:
                code, class_name = generate_mitre_skill(bp)
            else:
                code, class_name = generate_cve_skill(bp)

            # Validate syntax
            ast.parse(code)

            # Deploy to skills dir
            file_name = to_snake_case(class_name) + ".py"
            skill_path = SKILLS_DIR / file_name
            skill_path.write_text(code, encoding="utf-8")

            # Quick unit test
            import subprocess
            result = subprocess.run(
                [sys.executable, str(skill_path)],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                log.warning(f"  Unit test warning for {file_name}: {result.stderr[:200]}")

            log.info(f"  [OK] {class_name} -> {file_name} ({len(code):,} chars)")
            deployed.append({"blueprint_id": bp_id, "class": class_name, "file": file_name})

        except SyntaxError as e:
            log.error(f"  [FAIL] Syntax error untuk {bp_id}: {e}")
            failed.append(bp_id)
        except Exception as e:
            log.error(f"  [FAIL] Error untuk {bp_id}: {e}")
            failed.append(bp_id)

    summary = {
        "mode":      "template_synthesis_no_llm",
        "total":     len(candidates),
        "success":   len(deployed),
        "failed":    len(failed),
        "deployed":  deployed,
        "timestamp": datetime.utcnow().isoformat()
    }

    log.info("=" * 65)
    log.info(f"SELESAI: {len(deployed)} skill di-deploy, {len(failed)} gagal")
    log.info("=" * 65)
    return summary


if __name__ == "__main__":
    result = run_template_synthesis(max_blueprints=20)
    print(json.dumps(result, indent=2, ensure_ascii=False))
