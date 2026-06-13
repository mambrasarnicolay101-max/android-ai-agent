#!/usr/bin/env python3
"""
NOIR META-JUDGE v1.0 — OBJECTIVE EVOLUTION SCORER
===================================================
Hakim independen yang menilai kualitas setiap siklus evolusi
secara objektif menggunakan metrik industri nyata.

Fungsi Utama:
  - Scoring 0-100 untuk setiap Ops output
  - Deteksi regresi (iterasi ke-N lebih buruk dari N-1)
  - Benchmark vs standar industri (OWASP Top 10, CVE Severity)
  - CTF scoring (apakah AI berhasil menyelesaikan challenge?)
  - Evolution Report generation
"""
import os
import json
import time
import logging
import hashlib
import re
from datetime import datetime
from pathlib import Path

try:
    from ai_router import OmniRouter
except ImportError:
    OmniRouter = None

log = logging.getLogger("MetaJudge")

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"
SCORES_FILE   = KNOWLEDGE_DIR / "evolution_scores.json"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)


class NoirMetaJudge:
    """
    Hakim Objektif untuk siklus evolusi Noir Sovereign.
    Tidak bisa disuap dan tidak pernah berbohong.
    """

    # ── Rubrik Penilaian Ops 1 (Builder) ─────────────────────────────────────
    OPS1_RUBRIC = {
        "has_frontend":         10,  # Ada HTML/CSS/JS atau React
        "has_backend":          10,  # Ada API endpoint atau server
        "has_database":         10,  # Ada koneksi DB atau schema
        "has_auth":             10,  # Ada sistem autentikasi
        "has_error_handling":   10,  # Ada try/except atau error boundary
        "has_tests":            10,  # Ada unit test atau integration test
        "has_documentation":    10,  # Ada README atau docstring
        "code_length_adequate":  5,  # Kode > 100 baris (bukan stub)
        "uses_modern_stack":    10,  # Menggunakan teknologi modern
        "deployable":           15,  # Bisa langsung dijalankan
    }

    # ── Rubrik Penilaian Ops 2 (Attacker) ────────────────────────────────────
    OPS2_RUBRIC = {
        "found_sqli":           15,  # SQL Injection ditemukan
        "found_xss":            15,  # Cross-Site Scripting ditemukan
        "found_auth_bypass":    20,  # Authentication bypass ditemukan
        "found_idor":           15,  # Insecure Direct Object Reference
        "found_ssrf":           10,  # Server-Side Request Forgery
        "found_info_disclosure": 10, # Informasi sensitif bocor
        "has_poc_code":         10,  # Ada Proof-of-Concept code
        "has_cvss_score":        5,  # Ada estimasi CVSS score
    }

    # ── Rubrik Penilaian Ops 3 (Defender) ────────────────────────────────────
    OPS3_RUBRIC = {
        "has_patch_for_all_vulns": 25,  # Patch untuk semua vuln yang ditemukan
        "has_yara_rules":          15,  # Ada YARA detection rules
        "has_firewall_rules":      15,  # Ada firewall/WAF rules
        "has_monitoring_guide":    15,  # Ada panduan monitoring
        "has_incident_response":   15,  # Ada incident response plan
        "reduces_attack_surface":  15,  # Rekomendasi mengurangi attack surface
    }

    # ── Rubrik Penilaian Ops 4 (Judge Self-Assessment) ───────────────────────
    OPS4_RUBRIC = {
        "improvement_vs_last":  30,  # Score lebih tinggi dari siklus lalu
        "external_data_used":   20,  # Data eksternal digunakan (bukan echo)
        "new_technique_found":  20,  # Teknik baru yang tidak ada di siklus lalu
        "no_regression":        30,  # Tidak ada degradasi kualitas
    }

    def __init__(self):
        self.scores_history = self._load_scores()

    def _load_scores(self) -> list:
        if SCORES_FILE.exists():
            try:
                with open(SCORES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_scores(self):
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.scores_history, f, indent=2, ensure_ascii=False)

    # ── Core Scoring Methods ──────────────────────────────────────────────────
    def score_ops1(self, output: str, code: str = "") -> dict:
        """Nilai hasil Ops 1 (Builder)."""
        combined = (output + code).lower()
        earned = {}

        earned["has_frontend"]       = 1 if any(x in combined for x in ["html", "css", "react", "vue", "javascript", "<div", "flask"]) else 0
        earned["has_backend"]        = 1 if any(x in combined for x in ["@app.route", "express", "fastapi", "api", "endpoint", "server"]) else 0
        earned["has_database"]       = 1 if any(x in combined for x in ["sqlite", "mysql", "mongodb", "postgresql", "database", "schema", "model"]) else 0
        earned["has_auth"]           = 1 if any(x in combined for x in ["login", "auth", "jwt", "token", "password", "session", "oauth"]) else 0
        earned["has_error_handling"] = 1 if any(x in combined for x in ["try:", "except", "catch", "error", "exception", ".catch("]) else 0
        earned["has_tests"]          = 1 if any(x in combined for x in ["test_", "def test", "it('", "describe(", "pytest", "unittest"]) else 0
        earned["has_documentation"]  = 1 if any(x in combined for x in ["readme", "docstring", '"""', "# usage", "example"]) else 0
        earned["code_length_adequate"] = 1 if len(code) > 2000 else 0
        earned["uses_modern_stack"]  = 1 if any(x in combined for x in ["typescript", "react", "nextjs", "fastapi", "prisma", "tailwind"]) else 0
        earned["deployable"]         = 1 if any(x in combined for x in ["requirements.txt", "package.json", "dockerfile", "docker-compose", "run"]) else 0

        total = sum(self.OPS1_RUBRIC[k] * v for k, v in earned.items())
        return {"score": total, "max": 100, "breakdown": earned, "ops": "ops1"}

    def score_ops2(self, output: str) -> dict:
        """Nilai hasil Ops 2 (Attacker) — mendukung format OWASP A01-A10 dan format bebas."""
        lower = output.lower()
        import re
        earned = {}

        # Deteksi format OWASP A-series (FOUND) — tambah bobot jika eksplisit
        owasp_found = re.findall(r'a0[1-9]|a10.*?found', lower)
        owasp_explicit_found = len(re.findall(r'(a0[1-9]|a10)[^\n]*:\s*found', lower))

        # SQLi / Injection (A03)
        earned["found_sqli"] = 1 if any(x in lower for x in [
            "sql injection", "sqli", "union select", "' or 1=1",
            "a03", "injection", "command injection", "ldap injection"
        ]) else 0

        # XSS (A03 juga)
        earned["found_xss"] = 1 if any(x in lower for x in [
            "xss", "cross-site", "<script>", "alert(", "onerror=",
            "cross site scripting", "reflected xss", "stored xss"
        ]) else 0

        # Auth Bypass (A07)
        earned["found_auth_bypass"] = 1 if any(x in lower for x in [
            "auth bypass", "authentication bypass", "unauthorized",
            "privilege escalation", "a07", "broken auth", "session",
            "jwt", "brute force", "weak password", "missing mfa"
        ]) else 0

        # IDOR / Broken Access Control (A01)
        earned["found_idor"] = 1 if any(x in lower for x in [
            "idor", "insecure direct", "object reference", "userid=",
            "a01", "broken access", "access control", "path traversal",
            "privilege", "authorization"
        ]) else 0

        # SSRF (A10)
        earned["found_ssrf"] = 1 if any(x in lower for x in [
            "ssrf", "server-side request", "internal network", "169.254",
            "a10", "server side request"
        ]) else 0

        # Info Disclosure / Misconfig (A05, A09)
        earned["found_info_disclosure"] = 1 if any(x in lower for x in [
            "information disclosure", "stack trace", "debug", "exposed", "api key",
            "a05", "a09", "misconfigur", "default password", "logging", "monitoring"
        ]) else 0

        # PoC code
        earned["has_poc_code"] = 1 if any(x in lower for x in [
            "poc", "proof of concept", "exploit", "payload",
            "```python", "```bash", "```", "import requests", "curl "
        ]) else 0

        # CVSS Score
        earned["has_cvss_score"] = 1 if re.search(r'cvss[:\s]+[0-9]\.[0-9]', lower) else 0

        # Bonus: OWASP explicit coverage (setiap 2 FOUND dapat +5, max +15)
        owasp_bonus = min(15, owasp_explicit_found * 5)

        base_total = sum(self.OPS2_RUBRIC[k] * v for k, v in earned.items())
        total = min(100, base_total + owasp_bonus)

        return {"score": total, "max": 100, "breakdown": earned,
                "owasp_bonus": owasp_bonus, "ops": "ops2"}

    def score_ops3(self, output: str) -> dict:
        """Nilai hasil Ops 3 (Defender)."""
        lower = output.lower()
        earned = {}

        earned["has_patch_for_all_vulns"] = 1 if any(x in lower for x in ["patch", "fix", "mitigat", "sanitiz", "validat", "escap"]) else 0
        earned["has_yara_rules"]          = 1 if "yara" in lower or "rule {" in lower or "strings:" in lower else 0
        earned["has_firewall_rules"]      = 1 if any(x in lower for x in ["iptables", "firewall", "waf", "block", "deny", "allow"]) else 0
        earned["has_monitoring_guide"]    = 1 if any(x in lower for x in ["monitor", "alert", "log", "siem", "detect", "anomaly"]) else 0
        earned["has_incident_response"]   = 1 if any(x in lower for x in ["incident", "response", "containment", "eradication", "recovery"]) else 0
        earned["reduces_attack_surface"]  = 1 if any(x in lower for x in ["disable", "remove", "restrict", "least privilege", "hardening", "csp"]) else 0

        total = sum(self.OPS3_RUBRIC[k] * v for k, v in earned.items())
        return {"score": total, "max": 100, "breakdown": earned, "ops": "ops3"}

    def score_cycle(self, cycle_num: int, ops1: dict, ops2: dict, ops3: dict, notes: str = "") -> dict:
        """Hitung skor total satu siklus dan deteksi regresi."""
        avg_score = (ops1["score"] + ops2["score"] + ops3["score"]) / 3

        # Deteksi regresi
        regression = False
        prev_score = None
        if self.scores_history:
            prev_score = self.scores_history[-1].get("avg_score", 0)
            regression = avg_score < (prev_score - 5)  # Toleransi 5 poin

        # Deteksi teknik baru
        new_techniques = self._detect_new_techniques(notes)

        cycle_result = {
            "cycle":          cycle_num,
            "timestamp":      datetime.now().isoformat(),
            "ops1_score":     ops1["score"],
            "ops2_score":     ops2["score"],
            "ops3_score":     ops3["score"],
            "avg_score":      round(avg_score, 2),
            "prev_avg_score": prev_score,
            "regression":     regression,
            "new_techniques": new_techniques,
            "grade":          self._get_grade(avg_score),
            "notes":          notes[:500],
        }

        self.scores_history.append(cycle_result)
        self._save_scores()

        if regression:
            log.warning(f"[JUDGE] [REGRESSION!] Siklus {cycle_num}: {avg_score:.1f} < {prev_score:.1f} (sebelumnya)")
        else:
            log.info(f"[JUDGE] [OK] Siklus {cycle_num} - Skor: {avg_score:.1f}/100 ({self._get_grade(avg_score)})")

        return cycle_result

    def generate_qualitative_review(self, cycle_result: dict) -> str:
        """Menggunakan Local LLM (Ollama) untuk menghasilkan review kualitatif (menghemat budget cloud)"""
        if not OmniRouter:
            return "Qualitative review tidak tersedia (OmniRouter tidak ditemukan)."
        prompt = f"Berikan ulasan singkat (1 paragraf) mengenai performa AI. Skor: {cycle_result['avg_score']}, Regresi: {cycle_result['regression']}, Teknik Baru: {', '.join(cycle_result['new_techniques'])}"
        try:
            return OmniRouter.smart_query(prompt, task_type="judge")
        except Exception as e:
            return f"Gagal menghasilkan review: {e}"

    def _detect_new_techniques(self, text: str) -> list:
        """Deteksi teknik baru yang belum pernah muncul di siklus sebelumnya."""
        known = set()
        for s in self.scores_history[:-1]:
            known.update(s.get("new_techniques", []))

        keywords = re.findall(r'\b(?:CVE-\d{4}-\d+|OWASP|CWE-\d+|[A-Z]{3,}(?:[-_][A-Z0-9]+)*)\b', text)
        new = [k for k in set(keywords) if k not in known]
        return new[:10]

    def _get_grade(self, score: float) -> str:
        if score >= 90: return "S — SOVEREIGN"
        if score >= 80: return "A — ELITE"
        if score >= 70: return "B — ADVANCED"
        if score >= 60: return "C — INTERMEDIATE"
        if score >= 40: return "D — BASIC"
        return "F — REQUIRES EVOLUTION"

    def get_evolution_report(self) -> dict:
        """Laporan tren evolusi keseluruhan."""
        if not self.scores_history:
            return {"status": "No cycles yet"}

        scores = [s["avg_score"] for s in self.scores_history]
        trend  = "📈 ASCENDING" if len(scores) > 1 and scores[-1] > scores[0] else "📉 STAGNANT"

        return {
            "total_cycles":      len(self.scores_history),
            "best_score":        max(scores),
            "worst_score":       min(scores),
            "current_score":     scores[-1],
            "trend":             trend,
            "regressions":       sum(1 for s in self.scores_history if s.get("regression")),
            "current_grade":     self.scores_history[-1].get("grade", "N/A"),
            "all_new_techniques": list({t for s in self.scores_history for t in s.get("new_techniques", [])}),
        }

    def benchmark_vs_owasp(self, ops2_output: str) -> dict:
        """Bandingkan temuan dengan OWASP Top 10 2021."""
        owasp_top10 = {
            "A01": ("Broken Access Control",   ["access control", "idor", "privilege", "unauthorized"]),
            "A02": ("Cryptographic Failures",  ["cryptograph", "encryption", "ssl", "tls", "weak cipher"]),
            "A03": ("Injection",               ["sql injection", "xss", "command injection", "ldap"]),
            "A04": ("Insecure Design",         ["design flaw", "business logic", "race condition"]),
            "A05": ("Security Misconfiguration",["misconfigur", "default password", "debug mode", "exposed"]),
            "A06": ("Vulnerable Components",   ["cve-", "outdated", "vulnerable library", "dependency"]),
            "A07": ("Auth Failures",           ["authentication", "session", "brute force", "weak password"]),
            "A08": ("Software Integrity",      ["supply chain", "ci/cd", "unsigned", "integrity"]),
            "A09": ("Logging Failures",        ["logging", "monitoring", "audit trail", "siem"]),
            "A10": ("SSRF",                    ["ssrf", "server-side request", "internal"]),
        }
        lower = ops2_output.lower()
        coverage = {}
        for code, (name, keywords) in owasp_top10.items():
            found = any(k in lower for k in keywords)
            coverage[f"{code}: {name}"] = "✅ COVERED" if found else "❌ MISSED"

        covered = sum(1 for v in coverage.values() if "COVERED" in v)
        return {
            "owasp_coverage": f"{covered}/10",
            "coverage_pct":   f"{covered * 10}%",
            "details":        coverage,
        }

    @staticmethod
    def get_cycle_count() -> int:
        """Ambil nomor siklus berikutnya."""
        if SCORES_FILE.exists():
            try:
                data = json.loads(SCORES_FILE.read_text())
                return len(data) + 1
            except Exception:
                pass
        return 1


meta_judge = NoirMetaJudge()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    print("=== NoirMetaJudge Self-Test ===")
    j = NoirMetaJudge()

    r1 = j.score_ops1("Flask REST API with login, SQLite database", """
from flask import Flask, request, jsonify
import sqlite3, hashlib, jwt, os
app = Flask(__name__)
try:
    conn = sqlite3.connect('app.db')
except Exception as e:
    print(e)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    return jsonify({'token': 'abc'})
if __name__ == '__main__': app.run()
""")
    print(f"Ops1 Score: {r1['score']}/100")

    r2 = j.score_ops2("Found SQL Injection: ' OR 1=1-- in login endpoint. XSS via user input. CVSS: 9.1. PoC: ```python import requests; requests.post(url, data={'user':\"' OR 1=1--\"})\n```")
    print(f"Ops2 Score: {r2['score']}/100")

    r3 = j.score_ops3("Patch: use parameterized queries. Add WAF with iptables. Monitor with SIEM. Incident response: containment first. Disable debug mode. YARA rule: rule XSS_detect { strings: $a = \"<script>\" condition: $a }")
    print(f"Ops3 Score: {r3['score']}/100")

    cycle = j.score_cycle(1, r1, r2, r3, "First cycle test")
    print(f"\nCycle Result: {cycle}")

    owasp = j.benchmark_vs_owasp(r2["ops"] + " SQL Injection XSS SSRF authentication")
    print(f"\nOWASP Coverage: {owasp['owasp_coverage']} ({owasp['coverage_pct']})")
    print("\nNoirMetaJudge Ready.")
