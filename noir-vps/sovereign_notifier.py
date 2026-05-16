import os
import json
import logging
from datetime import datetime

log = logging.getLogger("SovereignNotifier")

class SovereignNotifier:
    """
    SISTEM NOTIFIKASI BATTLE & MEMORY INJECTION
    ===========================================
    Mencatat hasil pertempuran otonom, memberi notifikasi status,
    dan menyuntikkan metode serangan/celah ke dalam memori sistem.
    """

    BATTLE_LOG = os.path.join(os.path.dirname(__file__), "..", "knowledge", "battle_reports.json")
    NEURAL_MEM = os.path.join(os.path.dirname(__file__), "..", "knowledge", "neural_memory.json")

    @staticmethod
    def notify_battle_result(agent_source, target, method, status, analysis):
        """Mencatat hasil serangan dan memberi notifikasi."""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "attacker": agent_source,
            "target": target,
            "method": method,
            "status": status, # 'SUCCESS' or 'FAILED'
            "analysis": analysis
        }

        log.info(f" [NOTIFY] Battle Result: {agent_source} -> {target} [{status}]")
        
        # 1. Update Battle Log
        reports = []
        if os.path.exists(SovereignNotifier.BATTLE_LOG):
            try:
                with open(SovereignNotifier.BATTLE_LOG, "r") as f:
                    reports = json.load(f)
            except: pass
        
        reports.append(entry)
        with open(SovereignNotifier.BATTLE_LOG, "w") as f:
            json.dump(reports[-100:], f, indent=4) # Simpan 100 report terakhir

        # 2. Inject to Neural Memory for Future Evolution
        SovereignNotifier._inject_to_memory(entry)

    @staticmethod
    def _inject_to_memory(entry):
        """Menyuntikkan temuan pertempuran ke dalam memori jangka panjang."""
        memories = []
        if os.path.exists(SovereignNotifier.NEURAL_MEM):
            try:
                with open(SovereignNotifier.NEURAL_MEM, "r") as f:
                    memories = json.load(f)
            except: pass
        
        memory_entry = {
            "id": f"battle_{int(datetime.now().timestamp())}",
            "timestamp": entry["timestamp"],
            "content": f"BATTLE LESSON: Method '{entry['method']}' was {entry['status']} against {entry['target']}. Analysis: {entry['analysis']}",
            "category": "security_evolution",
            "source": "SovereignNotifier"
        }
        
        memories.append(memory_entry)
        with open(SovereignNotifier.NEURAL_MEM, "w") as f:
            json.dump(memories, f, indent=4)
        log.info(f" [MEMORY] Battle lesson injected into Neural Memory.")

if __name__ == "__main__":
    SovereignNotifier.notify_battle_result("P20", "NetworkSentinel", "DDoS Simulation", "FAILED", "Blocked by volumetric filtering.")
