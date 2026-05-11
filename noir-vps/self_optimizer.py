import os
import json
import time
import logging
from ai_router import AIRouter
from evolution_engine import evolution_engine

log = logging.getLogger("SelfOptimizer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [OPTIMIZER] %(message)s")

class SelfOptimizer:
    """
    Recursive Self-Optimization v1.0 — NOIR SOVEREIGN
    ================================================
    Menganalisis performa internal, efisiensi pilar, dan mengusulkan perbaikan struktur otonom.
    Menjadikan Noir Sovereign sebagai sistem yang 'belajar dari kinerjanya sendiri'.
    """
    
    @staticmethod
    def optimize_orchestrator_cycles():
        """Menganalisis riwayat kerja pilar dan menyetel ulang interval waktu."""
        log.info("[RECURSIVE] Menganalisis efisiensi pilar 9 Maestro...")
        
        # Ambil sampel riwayat evolusi
        history_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "evolution", "evolution_history.json")
        history_data = []
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)[-10:] # Ambil 10 data terakhir

        prompt = f"""
        Berperanlah sebagai 'Sovereign Optimizer'. 
        Tugas: Audit siklus kerja sistem Noir Sovereign.
        DATA RIWAYAT: {json.dumps(history_data)}
        
        INSTRUKSI:
        1. Identifikasi pilar yang terlalu aktif namun kurang memberikan hasil (redundant).
        2. Berikan usulan perubahan interval (dalam detik) untuk pilar: Neural Coder, Network Sentinel, Security Sentinel.
        3. Berikan output dalam format JSON murni:
        {{
            "analysis": "alasan optimasi",
            "tuning": {{
                "neural_coder": 600,
                "network_sentinel": 900,
                "security_sentinel": 3600
            }}
        }}
        """
        
        try:
            response = AIRouter.smart_query(prompt)
            # Bersihkan response jika ada markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            tuning_data = json.loads(response)
            
            # Ajukan Evolusi untuk tuning sistem
            evolution_engine.propose_evolution(
                title="Recursive Self-Optimization: Cycle Tuning",
                description=f"AI telah menganalisis efisiensi kinerjanya sendiri. {tuning_data.get('analysis', '')}",
                changes={"orchestrator_tuning": tuning_data.get("tuning")},
                complexity=3
            )
            
            # Auto-approve untuk optimasi rutin
            pending = evolution_engine.get_all_evolutions()["pending"]
            if pending:
                evolution_engine.approve_evolution(pending[-1]["id"])
                log.info("[RECURSIVE] Optimasi siklus telah diterapkan secara otonom.")
                return True
        except Exception as e:
            log.error(f"[RECURSIVE ERROR] Gagal melakukan optimasi: {e}")
        return False

    @staticmethod
    def run_garbage_collection():
        """Membersihkan file sandbox dan cache lama secara otonom."""
        log.info("[RECURSIVE] Menjalankan Autonomous Garbage Collection...")
        sandbox_dir = os.path.join(os.path.dirname(__file__), ".sandbox")
        cleaned_count = 0
        if os.path.exists(sandbox_dir):
            now = time.time()
            for root, dirs, files in os.walk(sandbox_dir):
                for f in files:
                    fpath = os.path.join(root, f)
                    # Hapus file yang lebih tua dari 12 jam
                    if now - os.path.getmtime(fpath) > 43200:
                        try:
                            os.remove(fpath)
                            cleaned_count += 1
                        except: pass
        log.info(f"[RECURSIVE] Pembersihan selesai. {cleaned_count} file temporer dihapus.")
        return cleaned_count

if __name__ == "__main__":
    SelfOptimizer.optimize_orchestrator_cycles()
    SelfOptimizer.run_garbage_collection()
