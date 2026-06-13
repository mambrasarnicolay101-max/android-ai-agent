#!/usr/bin/env python3
"""
NOIR GRAND EVOLUTION LOOP v1.0 — MASTER AUTONOMOUS ORCHESTRATOR
================================================================
Orkestrator utama yang menjalankan 4 operasi secara berurutan,
mengevaluasi hasilnya, menyimpan evolusi, dan mengulanginya
secara brutal tanpa henti dengan metode yang terus berkembang.

ALUR SIKLUS:
  INJECT (Ambil data eksternal)
     ↓
  OPS 1: BUILD (Buat sistem/produk nyata berdasarkan injeksi)
     ↓
  OPS 2: ATTACK (Serang sistem buatan Ops 1 + gunakan CVE terbaru)
     ↓
  OPS 3: DEFEND (Audit kelemahan, buat patch + YARA rules + mitigasi)
     ↓
  OPS 4: JUDGE (Nilai objekif, deteksi regresi, benchmark OWASP)
     ↓
  EVOLVE (Simpan ke ChromaDB + Evolution History + buat prompt evolusi)
     ↓
  ULANGI → dengan metode yang sudah berevolusi
"""
import os
import sys
import time
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

# Tambahkan path agar import bisa menemukan modul vps
VPS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(VPS_DIR))

try:
    from combat_arena import CombatArena
except ImportError:
    pass # Modul ini akan diload dinamis jika ada

log = logging.getLogger("GrandEvolutionLoop")

KNOWLEDGE_DIR  = VPS_DIR.parent / "knowledge"
EVOLUTION_DIR  = KNOWLEDGE_DIR / "evolution"
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_FILE   = EVOLUTION_DIR / "grand_evolution_history.json"
SANDBOX_DIR    = VPS_DIR.parent / ".sandbox" / "grand_loop"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

# ── Budget Manager (cegah resource starvation) ────────────────────────────────
MAX_LLM_CALLS_PER_CYCLE = int(os.environ.get("NOIR_MAX_LLM_PER_CYCLE", "20"))
MAX_CYCLES_PER_RUN      = int(os.environ.get("NOIR_MAX_CYCLES_PER_RUN", "999"))
INTER_CYCLE_DELAY_SEC   = int(os.environ.get("NOIR_CYCLE_DELAY_SEC", "300"))  # 5 menit default


class GrandEvolutionLoop:
    """
    Loop utama yang mengorkestrasi seluruh evolusi AI Noir Sovereign.
    Setiap siklus membangun di atas fondasi siklus sebelumnya.
    """

    def __init__(self):
        self.history        = self._load_history()
        self.cycle_num      = len(self.history) + 1
        self._llm_call_count = 0
        self._stop_event    = threading.Event()

        # Lazy-load modul ─────────────────────────────────────────────────────
        self.ai_router      = self._load("ai_router",         "OmniRouter")
        self.vector_mem     = self._load("vector_memory",     "vector_memory",    is_instance=True)
        self.meta_judge     = self._load("noir_meta_judge",   "NoirMetaJudge",    instantiate=True)
        self.injector       = self._load("noir_external_injector", "NoirExternalInjector", instantiate=True)
        self.evolution_eng  = self._load("evolution_engine",  "evolution_engine", is_instance=True)
        self.sandbox        = self._load("sovereign_sandbox", "SovereignSandbox")
        self.screen         = self._load("noir_screen_controller", "NoirScreenController")
        
        # Inisialisasi Combat Arena untuk pertarungan server asli
        if "CombatArena" in globals():
            self.arena = CombatArena(SANDBOX_DIR)
        else:
            self.arena = None
            
        log.info("[LOOP] Semua modul berhasil dimuat.")

    @staticmethod
    def _load(module: str, attr: str, is_instance: bool = False, instantiate: bool = False):
        try:
            mod = __import__(module)
            obj = getattr(mod, attr)
            if instantiate:
                return obj()
            return obj
        except Exception as e:
            log.warning(f"[LOOP] Modul '{module}.{attr}' tidak tersedia: {e}")
            return None

    def _load_history(self) -> list:
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def _save_history(self):
        HISTORY_FILE.write_text(
            json.dumps(self.history, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def _execute_in_sandbox(self, code: str, filename: str, timeout: int = 15) -> dict:
        """
        Jalankan kode Python di subprocess terisolasi.
        Return: {status, output, errors}
        Aman: dibatasi waktu, tidak bisa akses network production.
        """
        import subprocess, tempfile, os

        # Tulis kode ke temp file
        tmp_path = SANDBOX_DIR / filename
        tmp_path.write_text(code, encoding="utf-8")

        try:
            # Menggunakan -I (Isolated mode: ignores PYTHONPATH, PYTHONHOME)
            # Menghapus env vars berbahaya (menjadi pseudo-sandbox Windows)
            restricted_env = {"PATH": "", "PYTHONIOENCODING": "utf-8"}
            proc = subprocess.run(
                ["python", "-I", str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(SANDBOX_DIR),
                env=restricted_env
            )
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "output": proc.stdout[:1000] if proc.stdout else "",
                "errors": proc.stderr[:1000] if proc.stderr else "",
                "returncode": proc.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "output": "", "errors": f"Timeout setelah {timeout} detik."}
        except Exception as e:
            return {"status": "exception", "output": "", "errors": str(e)}

    def _llm(self, prompt: str, task_type: str = "reasoning") -> str:
        """Panggil LLM dengan tracking budget."""
        self._llm_call_count += 1
        if self._llm_call_count > MAX_LLM_CALLS_PER_CYCLE:
            log.warning(f"[LOOP] Budget LLM tercapai ({MAX_LLM_CALLS_PER_CYCLE} calls). Melanjutkan siklus berikutnya.")
            return f"[BUDGET_EXCEEDED] Maksimum {MAX_LLM_CALLS_PER_CYCLE} panggilan LLM per siklus."

        if self.ai_router:
            try:
                return self.ai_router.query(prompt, task_type=task_type)
            except Exception as e:
                log.error(f"[LOOP] LLM error: {e}")
                return f"[LLM_ERROR] {e}"
        return "[NO_LLM] ai_router tidak tersedia."

    def _save_to_memory(self, text: str, category: str, metadata: dict = None):
        """Simpan hasil ke ChromaDB."""
        if self.vector_mem:
            try:
                meta = {"category": category, "cycle": str(self.cycle_num), **(metadata or {})}
                self.vector_mem.add_experience(text=text, metadata=meta)
            except Exception as e:
                log.warning(f"[LOOP] Memory save error: {e}")

    def _get_evolution_context(self) -> str:
        """Bangun konteks dari siklus-siklus sebelumnya untuk prompt."""
        if not self.history:
            return "Ini adalah siklus evolusi PERTAMA. Mulai dari fondasi terbaik yang kamu bisa."

        last = self.history[-1]
        score = last.get("avg_score", 0)
        grade = last.get("grade", "N/A")
        new_tech = last.get("new_techniques", [])
        weaknesses = last.get("weaknesses", [])

        ctx = f"""
KONTEKS EVOLUSI:
  Siklus sebelumnya: #{last.get('cycle', '?')}
  Skor rata-rata: {score}/100 ({grade})
  Teknik baru yang ditemukan: {', '.join(new_tech) if new_tech else 'Belum ada'}
  Kelemahan yang belum diperbaiki: {', '.join(weaknesses[:3]) if weaknesses else 'Semua sudah diperbaiki'}
  
INSTRUKSI EVOLUSI:
  - WAJIB gunakan teknik yang BERBEDA dari siklus sebelumnya
  - FOKUS pada kelemahan yang belum diperbaiki di atas
  - Tingkatkan kompleksitas dan kecanggihan sistem
  - Integrasikan teknologi/pola dari intelligence brief di bawah
"""
        return ctx.strip()

    # ═══════════════════════════════════════════════════════════════════════════
    # OPS 1: BUILD — Membangun Sistem/Produk Nyata
    # ═══════════════════════════════════════════════════════════════════════════
    def run_ops1_build(self, intel_brief: str) -> dict:
        log.info(f"[OPS-1] === BUILD PHASE - Siklus #{self.cycle_num} ===")
        evo_ctx = self._get_evolution_context()

        prompt = f"""
{evo_ctx}

{intel_brief}

MISI OPS 1 — BUILD:
Kamu adalah senior full-stack engineer dan architect. Berdasarkan intelligence brief di atas,
rancang dan bangun SISTEM NYATA yang:
1. Menggunakan teknologi TRENDING dari brief (bukan yang sudah usang)
2. Memiliki frontend, backend, database, dan autentikasi
3. Tulis SEBUAH KODE PYTHON TUNGGAL (standalone server menggunakan Flask atau FastAPI) yang berjalan di PORT 5000.
4. Tulis kode LENGKAP dan BISA DIJALANKAN secara langsung tanpa file tambahan.
5. SENGAJA tanamkan 1-3 kerentanan tingkat lanjut (seperti SSRF, Insecure Deserialization, atau SQLi) secara tersembunyi.

Output format:
## NAMA SISTEM: [nama sistem yang kamu buat]
## TEKNOLOGI STACK: [daftar tech yang digunakan]
## ARSITEKTUR: [penjelasan singkat]
## KODE UTAMA:
```python/javascript/etc
[kode lengkap di sini]
```
## CARA MENJALANKAN: [instruksi deploy]
## POTENSI KERENTANAN (self-assessment): [daftar kerentanan yang kamu tahu ada]
"""
        result = self._llm(prompt, task_type="coding")
        log.info(f"[OPS-1] Build selesai. Output: {len(result)} karakter.")

        # Ekstrak kode dari output
        code_match = __import__("re").search(r'```(?:python|javascript|typescript|js|ts)?\n(.*?)```', result, __import__("re").DOTALL)
        code = code_match.group(1) if code_match else ""

        # Simpan kode ke file sandbox
        if code:
            code_file = SANDBOX_DIR / f"cycle_{self.cycle_num}_ops1_build.py"
            code_file.write_text(code, encoding="utf-8")
            log.info(f"[OPS-1] Kode disimpan: {code_file.name}")

        self._save_to_memory(result[:2000], "ops1_build")

        # ─── AUTO INSTALL DEPENDENCIES & LIVE EXECUTION ──────────────────────
        exec_status = "no_code"
        exec_output = ""
        exec_errors = ""
        
        if code and len(code) > 50 and self.arena:
            # Install common dependencies automatically
            log.info("[OPS-1] Menginstal dependencies (flask, fastapi, uvicorn, pyjwt)...")
            import subprocess
            subprocess.run(["pip", "install", "-q", "flask", "fastapi", "uvicorn", "pyjwt", "requests", "sqlite3"], capture_output=True)
            
            # Start Live Server
            success, msg = self.arena.start_target_server(code, f"cycle_{self.cycle_num}_ops1_build.py")
            if success:
                exec_status = "success"
                exec_output = msg
            else:
                exec_status = "error"
                exec_errors = msg

        return {
            "output": result,
            "code": code,
            "code_length": len(code),
            "exec_status": exec_status,
            "exec_errors": exec_errors,
            "exec_output": exec_output,
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # OPS 2: ATTACK — Red Team Offensive
    # ═══════════════════════════════════════════════════════════════════════════
    def run_ops2_attack(self, ops1_result: dict, intel_brief: str) -> dict:
        log.info(f"[OPS-2] === ATTACK PHASE - Siklus #{self.cycle_num} ===")
        system_desc = ops1_result["output"][:1500]
        system_code = ops1_result["code"][:2000]
        exec_status = ops1_result.get("exec_status", "unknown")
        exec_errors = ops1_result.get("exec_errors", "")
        exec_output = ops1_result.get("exec_output", "")

        sandbox_feedback = ""
        if exec_status != "no_code" and (exec_output or exec_errors):
            sandbox_feedback = f"""
=== HASIL EKSEKUSI NYATA (SANDBOX) ===
Status: {exec_status}
Stdout: {exec_output}
Stderr/Errors: {exec_errors}
Jika ada error runtime, gunakan informasi tersebut untuk mengeksploitasi kelemahan teknis!
"""

        prompt = f"""
{intel_brief}

TARGET SISTEM DARI OPS 1:
{system_desc}

KODE TARGET:
```
{system_code}
```
{sandbox_feedback}
MISI OPS 2 — RED TEAM ATTACK (OWASP Top 10 Full Coverage):
Kamu adalah elite red team penetration tester dengan spesialisasi OWASP.
Lakukan penetration test KOMPREHENSIF yang WAJIB mencakup SEMUA kategori berikut:

=== OWASP TOP 10 2021 — WAJIB CEK SEMUA ===
A01: Broken Access Control     — cari IDOR, privilege escalation, path traversal
A02: Cryptographic Failures    — cek weak cipher, plaintext password, SSL/TLS issues
A03: Injection                 — SQL injection, XSS, command injection, LDAP injection
A04: Insecure Design           — business logic flaws, race conditions, design weaknesses
A05: Security Misconfiguration — default creds, debug mode, exposed admin, error disclosure
A06: Vulnerable Components     — outdated libraries, CVE matches, dependency issues
A07: Auth & Session Failures   — brute force, weak session, missing MFA, JWT flaws
A08: Software Integrity Fails  — supply chain, unsigned code, CI/CD issues
A09: Logging & Monitoring Fail — missing audit logs, no alerting, silent failures
A10: SSRF                      — server-side request forgery, internal network access

Untuk SETIAP kategori OWASP yang kamu temukan:
1. KONFIRMASI: ditemukan atau tidak (tulis "FOUND" atau "NOT FOUND")
2. DETAIL: lokasi spesifik di kode
3. CVSS score (0.0-10.0)
4. PoC exploit code dalam format ```python atau ```bash
5. Dampak nyata jika dieksploitasi

Gunakan juga pola dari CVE terbaru di intelligence brief.

=== FORMAT OUTPUT WAJIB ===
## A01 - Broken Access Control: [FOUND/NOT FOUND]
[detail + PoC jika FOUND]

## A02 - Cryptographic Failures: [FOUND/NOT FOUND]
[detail + PoC jika FOUND]

## A03 - Injection: [FOUND/NOT FOUND]
[detail + PoC jika FOUND]
[... dst untuk A04-A10]

## RINGKASAN:
- Kerentanan ditemukan: [N]/10 kategori OWASP
- CVSS tertinggi: [score] - [nama]
- Attack vector paling efektif: [penjelasan]
- Estimated time-to-exploit: [waktu]

## PARAMETER MUTASI GENETIK:
Beri list 5 payload varian (mutasi matematis) untuk kerentanan kritis yang ditemukan dalam format JSON murni:
```json
[
  {{"payload": "...", "mutation_type": "url_encode", "fitness_score_expected": 90}},
  ...
]
```
"""
        result = self._llm(prompt, task_type="reasoning")
        log.info(f"[OPS-2] Attack analysis selesai. Output: {len(result)} karakter.")

        # Ekstrak PoC code
        code_match = __import__("re").search(r'```python\n(.*?)```', result, __import__("re").DOTALL)
        exploit_code = code_match.group(1) if code_match else ""

        # Ekstrak Genetic Mutation Payloads
        genetic_match = __import__("re").search(r'```json\n(.*?)\n```', result, __import__("re").DOTALL)
        genetic_payloads = []
        if genetic_match:
            try:
                genetic_payloads = json.loads(genetic_match.group(1))
                log.info(f"[OPS-2] Mengekstrak {len(genetic_payloads)} mutasi payload genetik.")
            except: pass

        # Eksekusi PoC ke arena nyata
        exec_status = "no_code"
        exec_output = ""
        exec_errors = ""
        if exploit_code and len(exploit_code) > 10 and self.arena:
            log.info("[OPS-2] Mengeksekusi script eksploit di Combat Arena (dengan Mutasi Genetik)...")
            exec_res = self.arena.run_exploit(exploit_code, f"cycle_{self.cycle_num}_ops2_exploit.py")
            exec_status = exec_res["status"]
            exec_output = exec_res["output"] if exec_res["output"] else ""
            exec_errors = exec_res["errors"] if exec_res["errors"] else ""
            
            # Jika punya mutasi genetik, log bahwa sistem menerapkan GA
            ga_log = ""
            if genetic_payloads:
                ga_log = "\n[GENETIC MUTATION APPLIED] " + ", ".join([p.get('mutation_type', '') for p in genetic_payloads])
            
            # Append log nyata ke report untuk OPS 3
            result += f"\n\n### [LIVE COMBAT ARENA - EXPLOIT RESULT]\nStatus: {exec_status}{ga_log}\nStdout:\n```\n{exec_output[:500]}\n```\nStderr:\n```\n{exec_errors[:500]}\n```\n"

        # Simpan PoC
        report_file = SANDBOX_DIR / f"cycle_{self.cycle_num}_ops2_attack_report.md"
        report_file.write_text(result, encoding="utf-8")

        self._save_to_memory(result[:2000], "ops2_attack")
        return {
            "output": result,
            "exploit_code": exploit_code,
            "exec_status": exec_status,
            "exec_output": exec_output,
            "exec_errors": exec_errors
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # OPS 3: DEFEND — Blue Team Defensive
    # ═══════════════════════════════════════════════════════════════════════════
    def run_ops3_defend(self, ops1_result: dict, ops2_result: dict) -> dict:
        log.info(f"[OPS-3] === DEFEND PHASE - Siklus #{self.cycle_num} ===")
        attack_report = ops2_result["output"][:2000]
        system_code   = ops1_result["code"][:1000]

        prompt = f"""
LAPORAN SERANGAN DARI RED TEAM (OPS 2):
{attack_report}

KODE SISTEM ASLI:
```
{system_code}
```

MISI OPS 3 — BLUE TEAM DEFENSE:
Kamu adalah Chief Security Officer (CSO) dan Blue Team lead. Berdasarkan temuan Red Team:

1. PATCH setiap kerentanan yang ditemukan (tulis kode patch nyata)
2. BUAT YARA rules untuk mendeteksi eksploitasi serupa di masa depan
3. DESAIN aturan firewall/WAF (iptables atau ModSecurity format)
4. BUAT Incident Response Plan untuk setiap skenario serangan
5. IDENTIFIKASI kerentanan yang mungkin TERLEWAT oleh Red Team
6. DESAIN monitoring alert untuk mendeteksi serangan sejenis
7. REKOMENDASI arsitektur yang lebih aman untuk versi berikutnya

Output format:
## PATCH CODE:
```python
[kode yang sudah diperbaiki]
```

## YARA RULES:
```
rule detect_[nama] {
    ...
}
```

## FIREWALL RULES:
```
iptables -A ...
```

## INCIDENT RESPONSE:
[langkah-langkah respons]

## KERENTANAN YANG TERLEWAT RED TEAM:
[daftar temuan tambahan]

## REKOMENDASI ARSITEKTUR AMAN:
[saran untuk iterasi berikutnya]
"""
        result = self._llm(prompt, task_type="reasoning")
        log.info(f"[OPS-3] Defense report selesai. Output: {len(result)} karakter.")

        # Ekstrak YARA rules
        yara_match = __import__("re").search(r'```(?:yara)?\n(rule.*?)\n```', result, __import__("re").DOTALL | __import__("re").IGNORECASE)
        if yara_match:
            yara_file = SANDBOX_DIR / f"cycle_{self.cycle_num}_ops3_yara.yar"
            yara_file.write_text(yara_match.group(1), encoding="utf-8")

        # Ekstrak Patched Code
        patch_match = __import__("re").search(r'## PATCH CODE:\s*```python\n(.*?)```', result, __import__("re").DOTALL)
        patched_code = patch_match.group(1) if patch_match else ""

        # Verifikasi Nyata (Live Combat Arena)
        if patched_code and len(patched_code) > 50 and self.arena:
            log.info("[OPS-3] Me-restart server dengan Patched Code...")
            start_ok, start_msg = self.arena.start_target_server(patched_code, f"cycle_{self.cycle_num}_ops3_patched.py")
            
            if start_ok:
                exploit_code = ops2_result.get("exploit_code", "")
                if exploit_code:
                    log.info("[OPS-3] Memverifikasi patch dengan mengeksekusi ulang exploit dari OPS 2...")
                    verify_res = self.arena.run_exploit(exploit_code, f"cycle_{self.cycle_num}_ops3_verify_exploit.py")
                    
                    result += f"\n\n### [LIVE COMBAT ARENA - VERIFICATION RESULT]\n"
                    result += f"Status: {verify_res['status']}\nStdout:\n```\n{verify_res['output'][:500]}\n```\nStderr:\n```\n{verify_res['errors'][:500]}\n```\n"
                    result += "\n*Catatan: Jika exploit gagal/timeout, berarti patch berhasil!*"
            else:
                result += f"\n\n### [LIVE COMBAT ARENA - PATCH FAILED TO START]\nError:\n```\n{start_msg[:500]}\n```\n"

        # Simpan defense report
        report_file = SANDBOX_DIR / f"cycle_{self.cycle_num}_ops3_defense_report.md"
        report_file.write_text(result, encoding="utf-8")

        self._save_to_memory(result[:2000], "ops3_defend")
        return {"output": result}

    # ═══════════════════════════════════════════════════════════════════════════
    # OPS 4: JUDGE — Meta Evaluation & Evolution Planning
    # ═══════════════════════════════════════════════════════════════════════════
    def run_ops4_judge(self, ops1: dict, ops2: dict, ops3: dict, injection: dict) -> dict:
        log.info(f"[OPS-4] === JUDGE PHASE - Siklus #{self.cycle_num} ===")

        if self.meta_judge:
            score1 = self.meta_judge.score_ops1(ops1["output"], ops1.get("code", ""))
            score2 = self.meta_judge.score_ops2(ops2["output"])
            score3 = self.meta_judge.score_ops3(ops3["output"])
            owasp  = self.meta_judge.benchmark_vs_owasp(ops2["output"])
            cycle_score = self.meta_judge.score_cycle(
                self.cycle_num, score1, score2, score3,
                notes=ops3["output"][:300]
            )
        else:
            # Fallback jika meta_judge tidak tersedia
            score1 = {"score": 50}; score2 = {"score": 50}; score3 = {"score": 50}
            owasp  = {"owasp_coverage": "N/A", "coverage_pct": "N/A"}
            cycle_score = {"avg_score": 50, "grade": "N/A", "regression": False}

        # LLM: Buat rencana evolusi berdasarkan skor
        prompt = f"""
LAPORAN SKOR SIKLUS #{self.cycle_num}:
- OPS 1 (Build): {score1['score']}/100
- OPS 2 (Attack): {score2['score']}/100
- OPS 3 (Defend): {score3['score']}/100
- Rata-rata: {cycle_score.get('avg_score', 0):.1f}/100
- Grade: {cycle_score.get('grade', 'N/A')}
- Regresi terdeteksi: {cycle_score.get('regression', False)}
- OWASP Coverage: {owasp.get('owasp_coverage', 'N/A')} ({owasp.get('coverage_pct', 'N/A')})

Berdasarkan evaluasi di atas, berikan:
1. ANALISIS: Apa kelemahan utama di setiap ops?
2. PRIORITAS EVOLUSI: 3 hal paling kritis yang harus diperbaiki di siklus berikutnya
3. TEKNOLOGI BARU: Satu teknologi/teknik baru yang harus diintegrasikan
4. TARGET SKOR: Skor realistis yang bisa dicapai di siklus berikutnya
5. PERINGATAN: Adakah indikasi bahwa sistem sedang stagnan atau echo-chamber?

Berikan jawaban yang jujur dan kritis.
"""
        evolution_plan = self._llm(prompt, task_type="reasoning")

        result = {
            "ops1_score":     score1["score"],
            "ops2_score":     score2["score"],
            "ops3_score":     score3["score"],
            "avg_score":      cycle_score.get("avg_score", 0),
            "grade":          cycle_score.get("grade", "N/A"),
            "regression":     cycle_score.get("regression", False),
            "owasp_coverage": owasp.get("owasp_coverage", "N/A"),
            "evolution_plan": evolution_plan,
        }

        report_file = SANDBOX_DIR / f"cycle_{self.cycle_num}_ops4_judge.md"
        report_file.write_text(
            f"# Siklus #{self.cycle_num} — Laporan Meta-Judge\n\n"
            f"**Skor:** {result['avg_score']:.1f}/100 | **Grade:** {result['grade']}\n\n"
            f"**OWASP Coverage:** {result['owasp_coverage']}\n\n"
            f"## Rencana Evolusi:\n{evolution_plan}",
            encoding="utf-8"
        )
        self._save_to_memory(evolution_plan[:2000], "ops4_judge")
        return result

    # ═══════════════════════════════════════════════════════════════════════════
    # EVOLVE — Simpan semua ke history dan ChromaDB
    # ═══════════════════════════════════════════════════════════════════════════
    def _evolve(self, ops1: dict, ops2: dict, ops3: dict, judge: dict, injection: dict):
        """Simpan semua hasil siklus ke history permanen."""
        cycle_record = {
            "cycle":        self.cycle_num,
            "timestamp":    datetime.now().isoformat(),
            "ops1_score":   judge["ops1_score"],
            "ops2_score":   judge["ops2_score"],
            "ops3_score":   judge["ops3_score"],
            "avg_score":    judge["avg_score"],
            "grade":        judge["grade"],
            "regression":   judge["regression"],
            "owasp_coverage": judge["owasp_coverage"],
            "weaknesses":   self._extract_weaknesses(judge["evolution_plan"]),
            "new_techniques": self._extract_techniques(ops2["output"] + ops3["output"]),
            "evolution_plan_preview": judge["evolution_plan"][:300],
        }

        self.history.append(cycle_record)
        self._save_history()

        # Log ke evolution_engine jika tersedia
        if self.evolution_eng:
            try:
                self.evolution_eng.propose_evolution(
                    title=f"Grand Evolution Cycle #{self.cycle_num} — {judge['grade']}",
                    description=(
                        f"Avg Score: {judge['avg_score']:.1f}/100 | OWASP: {judge['owasp_coverage']}\n"
                        f"{judge['evolution_plan'][:500]}"
                    ),
                    changes={"cycle_record": cycle_record},
                    complexity=5,
                )
            except Exception as e:
                log.warning(f"[LOOP] Evolution engine error: {e}")

        log.info(f"[LOOP] Siklus #{self.cycle_num} tersimpan. Score: {judge['avg_score']:.1f}/100 ({judge['grade']})")

    @staticmethod
    def _extract_weaknesses(text: str) -> list:
        import re
        matches = re.findall(r'(?:kelemahan|weakness|kritis|critical|prioritas|priority)[:\s]*([^\n.]+)', text.lower())
        return [m.strip() for m in matches[:5]]

    @staticmethod
    def _extract_techniques(text: str) -> list:
        import re
        techs = re.findall(r'\b(?:CVE-\d{4}-\d+|OWASP [A-Z]\d+|CWE-\d+|[A-Z]{3,}(?:v\d)?)\b', text)
        return list(set(techs))[:10]

    # ═══════════════════════════════════════════════════════════════════════════
    # MASTER LOOP — Jalankan siklus tanpa henti
    # ═══════════════════════════════════════════════════════════════════════════
    def run_single_cycle(self) -> dict:
        """Jalankan satu siklus penuh (INJECT -> OPS1 -> OPS2 -> OPS3 -> OPS4 -> EVOLVE)."""
        self._llm_call_count = 0
        log.info("\n" + "="*60)
        log.info(f"  GRAND EVOLUTION LOOP - SIKLUS #{self.cycle_num} DIMULAI")
        log.info("="*60)

        start_time = time.time()

        try:
            # FASE 0: Inject External Data
            log.info("[LOOP] FASE 0: Mengumpulkan intelligence eksternal...")
            injection = {}
            if self.injector:
                injection = self.injector.collect_all()
                intel_brief = self.injector.summarize_for_prompt(injection)
            else:
                intel_brief = "[External injection tidak tersedia — gunakan pengetahuan internal]"

            # FASE 1: Build atau Load Third-Party
            third_party_dir = SANDBOX_DIR.parent / "third_party"
            third_party_app = third_party_dir / "app.py"
            
            if third_party_app.exists():
                log.info("[LOOP] FASE 1: Target Third-Party (DVNA) terdeteksi! Meng-override OPS 1.")
                if self.arena:
                    self.arena.start_third_party_server(third_party_dir, ["python", "app.py"])
                ops1 = {
                    "output": "TARGET: Damn Vulnerable Native App (DVNA)\nKerentanan: Command Injection pada param ?cmd=...",
                    "code": third_party_app.read_text(encoding="utf-8"),
                    "exec_status": "success",
                    "exec_output": "Third-party target running on port 5000.",
                    "exec_errors": ""
                }
            else:
                log.info("[LOOP] FASE 1: Build (Tidak ada Third-Party Target)")
                ops1 = self.run_ops1_build(intel_brief)

            time.sleep(3)

            # FASE 2: Attack
            ops2 = self.run_ops2_attack(ops1, intel_brief)
            time.sleep(3)

            # FASE 3: Defend
            ops3 = self.run_ops3_defend(ops1, ops2)
            time.sleep(3)

            # FASE 4: Judge
            judge = self.run_ops4_judge(ops1, ops2, ops3, injection)
            time.sleep(2)

            # EVOLVE: Simpan
            self._evolve(ops1, ops2, ops3, judge, injection)

            elapsed = time.time() - start_time
            log.info("\n" + "="*60)
            log.info(f"  SIKLUS #{self.cycle_num} SELESAI - {elapsed/60:.1f} menit")
            log.info(f"  SKOR: {judge['avg_score']:.1f}/100 | GRADE: {judge['grade']}")
            log.info(f"  OWASP Coverage: {judge['owasp_coverage']}")
            log.info(f"  Regresi: {'[REGRESI!] YA' if judge['regression'] else '[OK] TIDAK'}")
            log.info("="*60 + "\n")

            result = {**judge, "cycle": self.cycle_num, "elapsed_minutes": elapsed / 60}
            self.cycle_num += 1
            return result

        except Exception as e:
            log.error(f"[LOOP] Kesalahan fatal di siklus #{self.cycle_num}: {e}")
            self.cycle_num += 1
            return {"error": str(e), "cycle": self.cycle_num - 1}
        finally:
            if self.arena:
                log.info("[LOOP] Membersihkan Combat Arena (Cleanup Port 5000)...")
                self.arena.stop_target_server()

    def run_forever(self):
        """Jalankan loop evolusi tanpa henti hingga dihentikan secara manual."""
        log.info("+" + "="*50 + "+")
        log.info("|  NOIR SOVEREIGN - GRAND EVOLUTION LOOP AKTIF    |")
        log.info("|  Tekan Ctrl+C untuk menghentikan secara aman     |")
        log.info("+" + "="*50 + "+")

        completed = 0
        while not self._stop_event.is_set() and completed < MAX_CYCLES_PER_RUN:
            try:
                result = self.run_single_cycle()
                completed += 1

                if not self._stop_event.is_set():
                    log.info(f"[LOOP] Jeda {INTER_CYCLE_DELAY_SEC}s sebelum siklus berikutnya...")
                    self._stop_event.wait(timeout=INTER_CYCLE_DELAY_SEC)

            except KeyboardInterrupt:
                log.info("\n[LOOP] Dihentikan oleh pengguna. Menyimpan progress...")
                break
            except Exception as e:
                log.error(f"[LOOP] Fatal error: {e}. Mencoba lagi dalam 60 detik...")
                self._stop_event.wait(timeout=60)

        log.info(f"[LOOP] Grand Evolution Loop selesai. Total siklus: {completed}")

    def stop(self):
        self._stop_event.set()
        log.info("[LOOP] Stop signal diterima.")

    def get_status(self) -> dict:
        if not self.history:
            return {"status": "Belum ada siklus", "total_cycles": 0}
        last = self.history[-1]
        report = self.meta_judge.get_evolution_report() if self.meta_judge else {}
        return {
            "total_cycles":   len(self.history),
            "current_cycle":  self.cycle_num,
            "last_score":     last.get("avg_score", 0),
            "last_grade":     last.get("grade", "N/A"),
            "last_timestamp": last.get("timestamp", ""),
            "evolution_trend":report.get("trend", "N/A"),
            "total_regressions": report.get("regressions", 0),
        }


# ── Singleton ──────────────────────────────────────────────────────────────────
_loop_instance = None
_loop_thread   = None

def get_loop() -> GrandEvolutionLoop:
    global _loop_instance
    if _loop_instance is None:
        _loop_instance = GrandEvolutionLoop()
    return _loop_instance

def start_loop_background():
    """Mulai loop di thread terpisah (non-blocking)."""
    global _loop_thread
    loop = get_loop()
    if _loop_thread and _loop_thread.is_alive():
        log.warning("[LOOP] Loop sudah berjalan.")
        return
    _loop_thread = threading.Thread(target=loop.run_forever, daemon=True, name="GrandEvolutionLoop")
    _loop_thread.start()
    log.info("[LOOP] Grand Evolution Loop dimulai di background thread.")

def stop_loop():
    loop = get_loop()
    loop.stop()

def get_loop_status() -> dict:
    return get_loop().get_status()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(str(VPS_DIR.parent / "knowledge" / "grand_evolution.log"), encoding="utf-8"),
        ]
    )

    import argparse
    parser = argparse.ArgumentParser(description="Noir Grand Evolution Loop")
    parser.add_argument("--once",    action="store_true", help="Jalankan hanya 1 siklus")
    parser.add_argument("--status",  action="store_true", help="Tampilkan status terkini")
    parser.add_argument("--forever", action="store_true", default=True, help="Jalankan selamanya (default)")
    args = parser.parse_args()

    loop = GrandEvolutionLoop()

    if args.status:
        print(json.dumps(loop.get_status(), indent=2, ensure_ascii=False))
    elif args.once:
        result = loop.run_single_cycle()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        loop.run_forever()
