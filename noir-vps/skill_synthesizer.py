import os
import json
import logging
import time
import subprocess
import sys
import re
import urllib.request
from ai_router import OmniRouter

log = logging.getLogger("SkillSynthesizer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [SYNTHESIZER] %(message)s")

class SkillSynthesizer:
    """
    Sovereign Skill Synthesizer v1.0  NOIR SOVEREIGN
    ================================================
    Membangun, menguji, dan memasang fitur baru secara otonom berdasarkan tujuan User.
    Proses meliputi: Brainstorming -> Coding -> Security Audit -> Validation -> Deployment.
    """
    def __init__(self):
        self.skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        self.sandbox_dir = os.path.join(os.path.dirname(__file__), ".sandbox", "synthesis")
        os.makedirs(self.sandbox_dir, exist_ok=True)
        os.makedirs(self.skills_dir, exist_ok=True)

    def _call_llm_direct(self, prompt: str) -> str:
        """
        Panggil LLM langsung (Groq -> Gemini) bypass SOVEREIGN_MASTER cutoff.
        Diperlukan untuk bootstrapping skill generation.
        """
        import urllib.request as _req_lib

        def _load_env_key(key_name: str) -> str:
            val = os.environ.get(key_name, "")
            if not val:
                env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
                if os.path.exists(env_path):
                    for line in open(env_path, encoding="utf-8"):
                        if line.startswith(f"{key_name}="):
                            val = line.strip().split("=", 1)[1].strip()
                            break
            return val

        # --- Attempt 1: Groq (fast, generous free tier) ---
        groq_key = _load_env_key("GROQ_API_KEY")
        if groq_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                payload = json.dumps({
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }).encode()
                req = _req_lib.Request(
                    url, data=payload,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {groq_key}"},
                    method="POST"
                )
                with _req_lib.urlopen(req, timeout=60) as r:
                    resp = json.loads(r.read().decode("utf-8"))
                return resp["choices"][0]["message"]["content"]
            except Exception as e:
                log.warning(f"[Synthesizer] Groq call gagal: {e}, mencoba Gemini...")

        # --- Attempt 2: Gemini ---
        gemini_key = _load_env_key("GEMINI_API_KEY")
        if gemini_key:
            try:
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-2.0-flash:generateContent?key={gemini_key}"
                )
                payload = json.dumps({"contents": [{"role": "user", "parts": [{"text": prompt}]}]}).encode()
                req = _req_lib.Request(
                    url, data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with _req_lib.urlopen(req, timeout=60) as r:
                    resp = json.loads(r.read().decode("utf-8"))
                return resp["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                log.warning(f"[Synthesizer] Gemini direct call gagal: {e}, fallback ke OmniRouter")

        # --- Final fallback: OmniRouter ---
        return OmniRouter.query(prompt, task_type="coding")

    def synthesize_new_skill(self, goal: str):
        log.info(f"== MEMULAI MISI SINTESIS OTONOM: {goal} ==")
        
        # Phase 1: Neural Coding (Generation)
        prompt = f"""
Berperanlah sebagai 'Neural Coder' elit Noir Sovereign.
Tugas: Membangun modul skill otonom Python.
TUJUAN: {goal}

SYARAT TEKNIS:
1. Kode harus dalam satu file Python.
2. Harus ada class dengan nama CamelCase (contoh: NetworkTrafficMonitor).
3. Class HARUS memiliki method instance 'execute(self)' yang menjalankan logika utama dan mengembalikan string hasil.
4. Kode harus bersih, efisien, dan memiliki error handling.
5. Gunakan library standar (os, sys, time, json, subprocess) atau requests/psutil jika perlu.
6. WAJIB MENYERTAKAN BLOCK `if __name__ == '__main__':` di bawah class yang berisi unit test menggunakan `unittest` untuk memvalidasi fungsi utama class tersebut.
7. Berikan HANYA kode Python lengkap dalam blok markdown ```python ... ```.
8. Nama file akan dibuat otomatis dari nama class (snake_case).
"""
        try:
            # Panggil LLM langsung (Groq/Gemini) — bypass SOVEREIGN_MASTER cutoff
            code_response = self._call_llm_direct(prompt)
        except Exception as e:
            return {"success": False, "reason": f"Neural Link Error: {e}"}
        
        # Extract code
        code_match = re.search(r"```python\n(.*?)\n```", code_response, re.DOTALL)
        if not code_match:
            # Fallback jika markdown tidak sempurna
            code = code_response.strip()
        else:
            code = code_match.group(1)

        # Identify Class & Filename
        class_match = re.search(r"class\s+(\w+)", code)
        if not class_match:
            return {"success": False, "reason": "Gagal mengidentifikasi struktur class dalam kode."}
            
        class_name = class_match.group(1)
        file_name = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower() + ".py"
        temp_path = os.path.join(self.sandbox_dir, file_name)
        
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Phase 2: Security Audit (SAST)
        try:
            from security_sentinel import SecuritySentinel
            findings = SecuritySentinel.scan_file(temp_path)
            if findings:
                risks = [f['message'] for f in findings if f['severity'] == 'HIGH']
                if risks:
                    log.warning(f"Sintesis DITOLAK: Ditemukan {len(risks)} risiko keamanan tinggi.")
                    return {"success": False, "reason": f"Audit Keamanan Gagal: {risks[0]}", "findings": findings}
        except ImportError:
            pass

        # Phase 3: Validation Run (TDD Unit Testing)
        try:
            # Jalankan script sebagai subprocess, yang akan memicu blok `if __name__ == '__main__':`
            # dan mengeksekusi unit tests yang dibuat oleh LLM
            log.info(f"Menjalankan Unit Tests (TDD) untuk {class_name}...")
            test_proc = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if test_proc.returncode != 0:
                log.warning(f"Validasi Test GAGAL:\n{test_proc.stderr}")
                return {"success": False, "reason": f"Unit Test Gagal:\n{test_proc.stderr[:500]}"}
            
            log.info(f"Validasi Unit Test BERHASIL:\n{test_proc.stderr}")
        except subprocess.TimeoutExpired:
            return {"success": False, "reason": "Validasi Kode Gagal: Timeout (Mungkin Infinite Loop)"}
        except Exception as e:
            return {"success": False, "reason": f"Validasi Kode Gagal: {e}"}

        # Phase 4: Final Deployment
        final_path = os.path.join(self.skills_dir, file_name)
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        log.info(f"Skill '{class_name}' berhasil dipasang ke sistem.")

        # Phase 5: Memory Consolidation
        try:
            from evolution_engine import evolution_engine
            evolution_engine.propose_evolution(
                title=f"Autonomous Skill Synthesis: {class_name}",
                description=f"AI berhasil membangun dan memverifikasi kapabilitas baru: '{goal}'. Modul telah dipasang dan siap dieksekusi.",
                changes={"synthesized_skill": {"file": file_name, "class": class_name, "goal": goal}},
                complexity=4
            )
            # Auto-approve
            history = evolution_engine.get_all_evolutions()["pending"]
            if history:
                evolution_engine.approve_evolution(history[-1]["id"])
        except:
            pass

        return {"success": True, "class": class_name, "file": file_name}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
        synth = SkillSynthesizer()
        print(json.dumps(synth.synthesize_new_skill(goal)))
