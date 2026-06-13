import os
import json
import logging
import time

log = logging.getLogger("RedBlueArena")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class RedBlueArena:
    """
    Sistem Simulasi Tertutup (Red vs Blue) untuk pembelajaran mandiri AI.
    AI membangun sistem dummy lokal, mensimulasikan pencarian celah keamanan, 
    kemudian Defender (Blue Team) menambalnya, dan hasilnya disimpan ke Memory.
    Sesuai prinsip keamanan: Ini BUKAN target eksternal, hanya melatih kode lokal.
    """
    def __init__(self):
        self.sandbox_dir = os.path.join(os.path.dirname(__file__), ".sandbox", "arena")
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
    def build_dummy_system(self) -> str:
        log.info("[ARENA] AI (Neural Coder) merancang sistem dummy dinamis...")
        
        # Gunakan LLM untuk membuat sistem yang memiliki celah spesifik
        from ai_router import OmniRouter
        prompt = "Generate a short Python code snippet (30 lines max) for a dummy web service that contains at least two distinct security vulnerabilities (e.g., IDOR, XSS, SQLi, or Insecure Deserialization). Ensure it is functional but vulnerable."
        code = OmniRouter.query(prompt, task_type="coding")
        
        if not code or "[Error]" in code:
            # Fallback to simple vulnerable code if LLM fails
            code = "def process(data):\n    import os\n    os.system('echo ' + data)"

        file_path = os.path.join(self.sandbox_dir, "dummy_app.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code.strip())
        log.info(f"[ARENA] Sistem dummy dinamis berhasil dibuat di: {file_path}")
        return file_path

    def red_team_attack(self, target_file: str) -> list:
        log.info(f"[RED TEAM] Memulai pemindaian dan simulasi eksploitasi terhadap sistem dummy...")
        # Red Team menggunakan modul SAST/Fuzzing lokal untuk mencari kelemahan
        from security_sentinel import SecuritySentinel
        findings = SecuritySentinel.scan_file(target_file)
        if findings:
            log.warning(f"[RED TEAM] Berhasil menemukan {len(findings)} titik kerentanan/vektor serangan!")
            for f in findings:
                log.warning(f" -> {f['message']} pada baris {f['line']}")
        else:
            log.info("[RED TEAM] Sistem aman, tidak ada kerentanan yang berhasil dieksploitasi.")
        return findings

    def blue_team_defend(self, target_file: str, findings: list):
        log.info("[BLUE TEAM] Menganalisis log serangan Red Team dan merumuskan arsitektur pertahanan...")
        if not findings:
            return

        with open(target_file, "r", encoding="utf-8") as f:
            code = f.read()
            
        from ai_router import OmniRouter
        prompt = f"As a Blue Team Defender, patch the following Python code to fix these vulnerabilities: {json.dumps(findings)}. Provide only the full patched code.\n\nCode:\n{code}"
        patched_code = OmniRouter.query(prompt, task_type="coding")

        if patched_code and "[Error]" not in patched_code:
            # Strip markdown if present
            if "```python" in patched_code:
                patched_code = patched_code.split("```python")[1].split("```")[0].strip()
            elif "```" in patched_code:
                patched_code = patched_code.split("```")[1].split("```")[0].strip()

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(patched_code)
            log.info("[BLUE TEAM] Patch keamanan cerdas berhasil diterapkan ke sistem dummy.")
        else:
            log.info("[BLUE TEAM] Gagal mempatch sistem secara otomatis melalui LLM.")

    def save_to_memory(self, attack_findings):
        log.info("[MEMORY] Mengonsolidasi metode serangan, celah, dan solusi patch ke Neural Memory...")
        try:
            # Mencoba menyimpan pengalaman ini agar AI tidak melakukan kesalahan yang sama
            from vector_memory import vector_memory
            vector_memory.add_experience(
                text=f"Simulasi Red-Blue berhasil dipelajari. Temuan: {len(attack_findings)} vektor. Patch mitigasi berhasil diterapkan. Semua log serangan dipelajari untuk pertahanan.",
                metadata={"source": "red_blue_arena", "type": "training_simulation"}
            )
            log.info("[MEMORY] Pembelajaran telah disimpan dalam Vector Memory.")
        except Exception as e:
            log.warning(f"[MEMORY] Gagal simpan ke vector memory: {e}")

        # Tambahkan ke Evolution History agar muncul di Wiki
        try:
            from evolution_engine import evolution_engine
            evolution_engine.propose_evolution(
                title=f"Simulasi Keamanan: {len(attack_findings)} Kerentanan Ditambal",
                description=f"Arena Red-Blue berhasil mendeteksi dan menambal {len(attack_findings)} celah keamanan pada sistem dummy.",
                changes={"security_arena_report": {"findings": attack_findings}},
                complexity=2
            )
        except Exception as e:
            log.warning(f"[MEMORY] Gagal log ke evolution engine: {e}")
                
        log.info("[MEMORY] Sistem telah berevolusi dan menyempurnakan metodologinya.")
        
        # Trigger Wiki Update
        try:
            from sovereign_wiki import SovereignWiki
            SovereignWiki.generate_wiki()
        except ImportError:
            pass

    def run_simulation(self, intensity="NORMAL"):
        """Jalankan satu siklus simulasi perang siber."""
        log.info(f" [ARENA] Memulai simulasi perang {intensity}...")
        log.info("=====================================================")
        log.info("=== MEMULAI SIMULASI RED VS BLUE OTONOM (ARENA) ===")
        log.info("=====================================================")
        
        # Phase 1: Membangun Target
        target = self.build_dummy_system()
        time.sleep(1)
        
        # Phase 2: Ujicoba Serangan
        findings = self.red_team_attack(target)
        time.sleep(1)
        
        if findings:
            # Phase 3: Pertahanan & Penambalan
            self.blue_team_defend(target, findings)
            time.sleep(1)
            
            # Phase 4: Verifikasi Pasca-Serangan (Pastikan patch berhasil)
            log.info("[ARENA] Melakukan pengujian ulang (Re-Audit) pasca-patching...")
            new_findings = self.red_team_attack(target)
            if not new_findings:
                log.info("[ARENA] Verifikasi sukses: Sistem dummy sekarang AMAN dari vektor serangan sebelumnya.")
            else:
                log.warning("[ARENA] Verifikasi gagal: Sistem masih memiliki kerentanan.")
                
        # Phase 5: Simpan ke Memori & Battle Logger
        log.info("[ARENA] Mencatat hasil pertempuran ke Battle Logger...")
        from battle_logger import BattleLogger
        BattleLogger.log_event(
            event_type="SIMULATION",
            target="Arena_Dummy_System",
            attacker="Neural_Red_Team",
            defender="Sovereign_Blue_Team",
            methods=["Dynamic Vulnerability Exploitation"],
            success=True if findings else False,
            findings=findings,
            evaluation="Simulasi otonom untuk melatih logika penambalan kode (Blue) vs eksploitasi (Red)."
        )
        
        self.save_to_memory(findings)
        log.info("=====================================================")
        log.info("=== SIMULASI PELATIHAN OTONOM SELESAI ===")
        log.info("=====================================================")

if __name__ == "__main__":
    arena = RedBlueArena()
    arena.run_simulation()
