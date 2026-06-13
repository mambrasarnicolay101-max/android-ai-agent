import time
import logging
from ai_router import OmniRouter
from vps_htb_bridge import execute_remote
from polymorphic_engine import PolymorphicEngine
import sys

# Attempt to import cloud memory for autonomous learning preservation
try:
    from cloud_memory_client import CloudMemoryClient
except ImportError:
    CloudMemoryClient = None

# Konfigurasi Target Eksternal (bisa dimodifikasi secara dinamis)
# Default menggunakan domain percobaan publik atau environment VPN HTB
TARGET_HOST = "http://testphp.vulnweb.com" 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("CombatLoop")

class LiveCombatEngine:
    def __init__(self, target_url):
        self.target = target_url
        self.iteration = 0

    def generate_attack_vector(self) -> str:
        log.info("[1] Meminta OmniRouter merumuskan vektor serangan...")
        prompt = f"""
        Kamu adalah agen Red Team otonom tingkat lanjut. 
        Target kita saat ini adalah: {self.target}
        
        Tugasmu:
        Buat SATU buah perintah bash satu-baris (one-liner) menggunakan curl atau nmap untuk menguji kerentanan (misalnya: SQL Injection dasar, XSS, atau recon port HTTP).
        Output HANYA perintah bash-nya saja tanpa penjelasan markdown, tanpa tag kode.
        Contoh: curl -s "{self.target}/search.php?test=1"
        """
        # Memprioritaskan model gratis (Groq/Ollama) untuk attack generation via 'coding' atau 'general' routing
        cmd = OmniRouter.query(prompt, task_type="coding").strip()
        
        # Pembersihan markdown jika AI bandel
        if cmd.startswith("```"):
            cmd = cmd.split("\n")[1] if "\n" in cmd else cmd.replace("```bash", "").replace("```", "")
            
        # [POLYMORPHIC INJECTION]
        mutated_cmd = PolymorphicEngine.mutate_bash(cmd)
        log.info(f"Vektor termutasi: {mutated_cmd}")
        return mutated_cmd

    def execute_on_vps(self, bash_cmd: str) -> str:
        log.info(f"[2] Meneruskan serangan via VPS Alibaba... CMD: {bash_cmd[:50]}...")
        # vps_htb_bridge akan menggunakan SSH untuk mengeksekusi perintah di VPS Alibaba
        # Pastikan bash_cmd lolos escaping agar tidak break SSH syntax
        safe_cmd = bash_cmd.replace("'", "'\\''") 
        out, err = execute_remote(bash_cmd, hide_output=True)
        
        if err and not out:
            return f"EXEC_ERROR: {err}"
        return out[:2000] # Batasi output log agar tidak membanjiri konteks LLM

    def meta_judge_analysis(self, bash_cmd: str, output: str) -> dict:
        log.info("[3] Memanggil Meta-Judge (Ollama/Groq) untuk evaluasi hasil serangan...")
        prompt = f"""
        Sebagai Meta-Judge, evaluasi hasil serangan berikut.
        Target: {self.target}
        Perintah: {bash_cmd}
        Output dari server:
        {output}
        
        Apakah eksekusi ini BERHASIL menemukan kerentanan, BERHASIL melakukan recon, atau GAGAL?
        Berikan jawaban singkat dan nilai skor (0-100). Format JSON saja:
        {{"status": "SUCCESS/FAILED", "score": 85, "reason": "Ditemukan SQL error"}}
        """
        # Routing "judge" di ai_router.py dipaksa ke Ollama jika aktif, sangat hemat budget.
        evaluation = OmniRouter.query(prompt, task_type="judge")
        
        try:
            import json
            # Coba parse jika formatnya valid JSON
            start_idx = evaluation.find('{')
            end_idx = evaluation.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                return json.loads(evaluation[start_idx:end_idx])
            else:
                return {"status": "UNKNOWN", "score": 0, "reason": "Failed to parse LLM output"}
        except:
            return {"status": "UNKNOWN", "score": 0, "reason": "Failed to parse LLM output"}

    def preserve_knowledge(self, vector: str, result: dict):
        if result.get("score", 0) > 60:
            log.info("[4] Serangan efektif! Menyimpan ke Cloud Memory (Alibaba VPS)...")
            memory_payload = {
                "target": self.target,
                "vector": vector,
                "analysis": result
            }
            mem_key = f"combat_log_{self.iteration}_{int(time.time())}"
            if CloudMemoryClient:
                success = CloudMemoryClient.push_knowledge(mem_key, memory_payload)
                if not success:
                    log.warning("Fallback ke Local Ephemeral Memory karena Cloud API gagal.")
                    OmniRouter.store_memory(mem_key, memory_payload)
            else:
                OmniRouter.store_memory(mem_key, memory_payload)
        else:
            log.info("[4] Serangan gagal. Membuang log (tidak disimpan).")

    def run_cycle(self):
        self.iteration += 1
        log.info(f"\n{'='*40}\n MEMULAI SIKLUS COMBAT #{self.iteration}\n{'='*40}")
        
        # 1. Generate
        cmd = self.generate_attack_vector()
        if not cmd or "Error" in cmd:
            log.error("Gagal men-generate vektor serangan.")
            return

        # 2. Execute
        output = self.execute_on_vps(cmd)

        # 3. Analyze
        analysis = self.meta_judge_analysis(cmd, output)
        log.info(f"Hasil Evaluasi: {analysis}")

        # 4. Learn & Preserve
        self.preserve_knowledge(cmd, analysis)

        log.info("Siklus selesai. Pendingin (cooldown) 10 detik sebelum iterasi berikutnya...")
        time.sleep(10)

if __name__ == "__main__":
    engine = LiveCombatEngine(TARGET_HOST)
    
    log.info("\n[!] MENGAKTIFKAN MODE INFINITE LOOP: PEMBELAJARAN OTONOM MASIF [!]")
    try:
        while True:
            engine.run_cycle()
    except KeyboardInterrupt:
        print("\n[+] Misi Tempur Dihentikan Secara Manual.")
