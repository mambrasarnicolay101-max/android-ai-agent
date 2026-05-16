import os
import json
import logging
import time
from datetime import datetime

log = logging.getLogger("SovereignMaturity")

class SovereignMaturityIndex:
    """
    SOVEREIGN MATURITY INDEX (SMI) v1.0
    ===================================
    Modul evaluasi diri otonom untuk memantau "tingkat kedewasaan" AI Agent.
    Menganalisis performa, stabilitas, dan kapasitas pembelajaran.
    """

    INDEX_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "maturity_index.json")

    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        os.makedirs(os.path.dirname(self.INDEX_FILE), exist_ok=True)

    def calculate_index(self) -> dict:
        """Melakukan audit internal dan menghitung skor maturitas."""
        log.info(" Initiating Sovereign Self-Evaluation...")

        # 1. Metrik Kapasitas (Knowledge & Skills)
        skill_count = self._count_skills()
        knowledge_size = self._get_knowledge_size()
        
        # 2. Metrik Stabilitas (Error Logs)
        stability_score = self._analyze_stability()
        
        # 3. Metrik Otonomi (Evolutions Applied)
        autonomy_score = self._analyze_autonomy()

        # Rumus Skor (0-100)
        # Weights: Capacity (30%), Stability (40%), Autonomy (30%)
        capacity_score = min(100, (skill_count * 5) + (knowledge_size // 1024))
        
        total_score = (capacity_score * 0.3) + (stability_score * 0.4) + (autonomy_score * 0.3)

        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": round(total_score, 2),
            "status": self._get_status_label(total_score),
            "metrics": {
                "capacity": {
                    "skill_count": skill_count,
                    "knowledge_kb": round(knowledge_size / 1024, 2),
                    "score": capacity_score
                },
                "stability": {
                    "score": stability_score,
                    "incident_count": self._count_recent_errors()
                },
                "autonomy": {
                    "score": autonomy_score,
                    "evolutions_total": self._count_evolutions()
                }
            },
            "recommendations": self._generate_recommendations(total_score, stability_score)
        }

        self._save_index(report)
        log.info(f" Self-Evaluation Complete. Maturity Score: {report['overall_score']}% [{report['status']}]")
        return report

    def _count_skills(self) -> int:
        skill_dir = os.path.join(self.base_dir, "noir-vps", "skills")
        if not os.path.exists(skill_dir): return 0
        return len([f for f in os.listdir(skill_dir) if f.endswith(".py")])

    def _get_knowledge_size(self) -> int:
        k_dir = os.path.join(self.base_dir, "knowledge")
        total = 0
        for root, dirs, files in os.walk(k_dir):
            for f in files:
                total += os.path.getsize(os.path.join(root, f))
        return total

    def _analyze_stability(self) -> float:
        """Menganalisis log untuk menentukan skor stabilitas."""
        error_count = self._count_recent_errors()
        # Semakin banyak error, skor semakin rendah (Base 100)
        return max(0, 100 - (error_count * 5))

    def _count_recent_errors(self) -> int:
        log_file = os.path.join(self.base_dir, "logs", "noir_agent.log")
        if not os.path.exists(log_file): return 0
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                return content.count("[ERROR]") + content.count("Critical")
        except: return 0

    def _analyze_autonomy(self) -> float:
        """Menganalisis riwayat evolusi."""
        evo_count = self._count_evolutions()
        return min(100, evo_count * 10)

    def _count_evolutions(self) -> int:
        history_file = os.path.join(self.base_dir, "knowledge", "evolution", "evolution_history.json")
        if not os.path.exists(history_file): return 0
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return len(json.load(f))
        except: return 0

    def _get_status_label(self, score: float) -> str:
        if score < 30: return "EMBRYONIC"
        if score < 60: return "DEVELOPING"
        if score < 85: return "MATURE"
        return "SOVEREIGN_MASTER"

    def _generate_recommendations(self, score: float, stability: float) -> list:
        recs = []
        if stability < 80:
            recs.append("Trigger 'Self-Healer' to analyze recurring crash patterns.")
            self._trigger_evolution_proposal(
                "Stability Optimization",
                f"Stability score is low ({stability}%). Requesting automated system hardening.",
                {"optimization": "stability_harden"}
            )
        if score < 50:
            recs.append("Increase 'Knowledge Absorption' frequency from external documentation.")
            self._trigger_evolution_proposal(
                "Knowledge Expansion",
                "Maturity index indicates low knowledge capacity. Requesting focused absorption cycle.",
                {"acquisition": "mass_absorption"}
            )
        if len(recs) == 0:
            recs.append("System is optimal. Proceed with recursive skill expansion.")
        return recs

    def _trigger_evolution_proposal(self, title: str, desc: str, changes: dict):
        """Memicu proposal evolusi otonom."""
        try:
            from evolution_engine import evolution_engine
            # Cek apakah proposal serupa sudah ada
            pending = evolution_engine.get_all_evolutions()["pending"]
            if any(p["title"] == title for p in pending):
                return # Skip jika sudah ada yang pending
            
            evolution_engine.propose_evolution(title, desc, changes, complexity=3)
            log.info(f" [SMI] Autonomous Evolution Proposed: {title}")
        except Exception as e:
            log.error(f"Failed to trigger evolution: {e}")

    def _save_index(self, report: dict):
        with open(self.INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    smi = SovereignMaturityIndex()
    print(json.dumps(smi.calculate_index(), indent=4))
