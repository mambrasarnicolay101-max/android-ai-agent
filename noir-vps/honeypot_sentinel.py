import os, json, time, logging
import random

log = logging.getLogger("HoneypotSentinel")

class HoneypotSentinel:
    """
    Pilar 21 - Honeypot Sentinel
    Menciptakan umpan (decoy) untuk menjebak penyerang dan mempelajari teknik mereka.
    """
    
    DECOY_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "honeypot_traps.json")

    @staticmethod
    def deploy_trap(trap_type="api_endpoint"):
        """Deploy a new decoy/trap."""
        traps = HoneypotSentinel._load_traps()
        
        trap_id = f"TRAP_{int(time.time())}"
        new_trap = {
            "id": trap_id,
            "type": trap_type,
            "deployed_at": time.time(),
            "status": "ACTIVE",
            "hits": 0,
            "details": {
                "url": f"/api/v1/admin/debug_{random.randint(1000, 9999)}",
                "purpose": "Decoy for unauthorized admin access attempts."
            }
        }
        
        traps.append(new_trap)
        HoneypotSentinel._save_traps(traps)
        log.info(f" [P21] Deployed {trap_type} trap: {trap_id}")
        return new_trap

    @staticmethod
    def record_hit(trap_id, intruder_data):
        """Record an interaction with a trap."""
        traps = HoneypotSentinel._load_traps()
        for t in traps:
            if t["id"] == trap_id:
                t["hits"] += 1
                t["last_hit"] = time.time()
                t["intruder_intel"] = intruder_data
                log.warning(f" [P21] ALERT! Trap {trap_id} triggered by {intruder_data.get('ip')}")
                break
        HoneypotSentinel._save_traps(traps)
        
        # Index to memory
        try:
            from vector_memory import vector_memory
            vector_memory.add_experience(
                f"Honeypot Triggered: {intruder_data.get('ip')} attempted access to {trap_id}",
                category="security_threat",
                metadata={"trap_id": trap_id, "intruder": intruder_data}
            )
        except: pass

    @staticmethod
    def _load_traps():
        if os.path.exists(HoneypotSentinel.DECOY_PATH):
            with open(HoneypotSentinel.DECOY_PATH, "r") as f:
                return json.load(f)
        return []

    @staticmethod
    def _save_traps(traps):
        os.makedirs(os.path.dirname(HoneypotSentinel.DECOY_PATH), exist_ok=True)
        with open(HoneypotSentinel.DECOY_PATH, "w") as f:
            json.dump(traps, f, indent=4)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    HoneypotSentinel.deploy_trap()
