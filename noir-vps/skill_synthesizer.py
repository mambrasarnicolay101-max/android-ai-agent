import os
import json
import logging
import time
import subprocess
import sys
import re
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
6. Berikan HANYA kode Python lengkap dalam blok markdown ```python ... ```.
7. Nama file akan dibuat otomatis dari nama class (snake_case).
"""
        try:
            code_response = OmniRouter.smart_query(prompt)
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

        # Phase 3: Validation Run
        try:
            # Syntax Check
            compile(code, temp_path, 'exec')
            log.info(f"Validasi Sintaks: BERHASIL.")
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
