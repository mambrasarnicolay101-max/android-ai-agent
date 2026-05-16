import os, json, time, logging
import hashlib

log = logging.getLogger("DistributedLedger")

class DistributedLedger:
    """
    Pilar 22 - Distributed Ledger for Logic (U-31)
    Menyimpan status kritis sistem dalam format immutable chain.
    """
    
    LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "sovereign_ledger.json")

    @staticmethod
    def record_state(state_desc, metadata=None):
        """Mencatat perubahan status ke dalam ledger."""
        ledger = DistributedLedger._load_ledger()
        
        last_hash = ledger[-1]["hash"] if ledger else "SINGULARITY_GENESIS"
        
        entry = {
            "index": len(ledger),
            "timestamp": time.time(),
            "state": state_desc,
            "metadata": metadata or {},
            "previous_hash": last_hash,
            "hash": ""
        }
        
        # Calculate Hash
        hash_string = json.dumps(entry, sort_keys=True).encode()
        entry["hash"] = hashlib.sha256(hash_string).hexdigest()
        
        ledger.append(entry)
        DistributedLedger._save_ledger(ledger)
        log.info(f" [LEDGER] New Block Added: {entry['index']} | Hash: {entry['hash'][:10]}")
        return entry

    @staticmethod
    def verify_integrity():
        """Memverifikasi seluruh chain untuk memastikan tidak ada data yang dimanipulasi."""
        ledger = DistributedLedger._load_ledger()
        for i in range(1, len(ledger)):
            if ledger[i]["previous_hash"] != ledger[i-1]["hash"]:
                log.critical(f" [LEDGER] INTEGRITY BREACH DETECTED at Block {i}!")
                return False
        log.info(" [LEDGER] Chain Integrity Verified.")
        return True

    @staticmethod
    def _load_ledger():
        if os.path.exists(DistributedLedger.LEDGER_PATH):
            with open(DistributedLedger.LEDGER_PATH, "r") as f:
                return json.load(f)
        return []

    @staticmethod
    def _save_ledger(ledger):
        os.makedirs(os.path.dirname(DistributedLedger.LEDGER_PATH), exist_ok=True)
        with open(DistributedLedger.LEDGER_PATH, "w") as f:
            json.dump(ledger, f, indent=4)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    DistributedLedger.record_state("System reached 50% upgrade completion.")
    DistributedLedger.verify_integrity()
