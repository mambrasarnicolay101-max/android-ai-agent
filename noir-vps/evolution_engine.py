import os, json, logging, uuid
from datetime import datetime, timedelta

log = logging.getLogger("EvolutionEngine")

class SovereignEvolutionEngine:
    """
    Sistem Pengembangan Diri Otonom v2.0
    Mengelola siklus evolusi kode dan skill secara otonom dengan kontrol mutlak User.
    FIX H-06: Load-before-write pattern untuk mencegah race condition antar thread.
    FIX M-05: Auto-expire proposals > 7 hari agar file tidak membengkak.
    """

    EVO_DIR      = os.path.join(os.path.dirname(__file__), "..", "knowledge", "evolution")
    PENDING_FILE = os.path.join(EVO_DIR, "pending_proposals.json")
    HISTORY_FILE = os.path.join(EVO_DIR, "evolution_history.json")
    PROPOSAL_TTL_DAYS = 7  # Proposal kedaluwarsa setelah 7 hari

    def __init__(self):
        os.makedirs(self.EVO_DIR, exist_ok=True)

    # ─── HELPERS ───
    def _load(self, path: str, default):
        """Load-before-write: selalu baca file terbaru dari disk."""
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return default

    def _save(self, path: str, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _expire_old_proposals(self, proposals: list) -> list:
        """FIX M-05: Hapus proposals yang melebihi TTL."""
        cutoff = (datetime.now() - timedelta(days=self.PROPOSAL_TTL_DAYS)).isoformat()
        active = [p for p in proposals if p.get("timestamp", "") >= cutoff]
        expired = len(proposals) - len(active)
        if expired:
            log.info(f"[EVO] Auto-expired {expired} proposal(s) yang lebih dari {self.PROPOSAL_TTL_DAYS} hari.")
        return active

    # ─── PUBLIC API ───
    def propose_evolution(self, title: str, description: str, changes: dict, complexity: int = 5) -> str:
        """Mendaftarkan proposal evolusi baru untuk persetujuan User."""
        # FIX H-06: Reload sebelum tulis agar tidak overwrite data dari thread lain
        pending = self._load(self.PENDING_FILE, [])
        pending = self._expire_old_proposals(pending)

        proposal = {
            "id":          str(uuid.uuid4())[:8],
            "timestamp":   datetime.now().isoformat(),
            "title":       title,
            "description": description,
            "changes":     changes,
            "complexity":  complexity,
            "status":      "PENDING_APPROVAL"
        }
        pending.append(proposal)
        self._save(self.PENDING_FILE, pending)
        log.info(f"[EVO] New proposal: {title} ({proposal['id']})")
        return proposal["id"]

    def approve_evolution(self, proposal_id: str) -> bool:
        """Menerapkan evolusi setelah mendapat izin mutlak dari User."""
        # FIX H-06: Reload fresh sebelum mutasi
        pending = self._load(self.PENDING_FILE, [])
        history = self._load(self.HISTORY_FILE, [])

        for i, prop in enumerate(pending):
            if prop["id"] == proposal_id:
                log.info(f"[EVO] USER APPROVED: {prop['title']}")
                success = self._execute_modification(prop)
                if success:
                    prop["status"]     = "APPLIED"
                    prop["applied_at"] = datetime.now().isoformat()
                    history.append(prop)
                    pending.pop(i)
                    self._save(self.PENDING_FILE, pending)
                    self._save(self.HISTORY_FILE, history)
                    
                    # Trigger Wiki Update
                    try:
                        from sovereign_wiki import SovereignWiki
                        SovereignWiki.generate_wiki()
                    except: pass
                    
                    # Trigger Mesh Sync (Broadcast to Mobile/PC)
                    try:
                        from mesh_sync import SovereignMesh
                        SovereignMesh.broadcast_knowledge(
                            title=prop.get("title"),
                            content=prop.get("changes"),
                            sync_type="applied_evolution"
                        )
                    except: pass
                    
                    return True
        return False

    def reject_evolution(self, proposal_id: str) -> bool:
        """Menolak evolusi dan menghapusnya dari antrian pending."""
        # FIX H-06: Reload fresh sebelum mutasi
        pending = self._load(self.PENDING_FILE, [])
        history = self._load(self.HISTORY_FILE, [])

        for i, prop in enumerate(pending):
            if prop["id"] == proposal_id:
                log.info(f"[EVO] USER REJECTED: {prop['title']}")
                prop["status"]      = "REJECTED"
                prop["rejected_at"] = datetime.now().isoformat()
                history.append(prop)
                pending.pop(i)
                self._save(self.PENDING_FILE, pending)
                self._save(self.HISTORY_FILE, history)
                return True
        return False

    def get_all_evolutions(self) -> dict:
        """Mengembalikan daftar semua proposal pending dan riwayat."""
        pending = self._expire_old_proposals(self._load(self.PENDING_FILE, []))
        history = self._load(self.HISTORY_FILE, [])
        return {"pending": pending, "history": history}

    def _execute_modification(self, proposal: dict) -> bool:
        """Logika teknis untuk menerapkan perubahan (Hot-fix, New File, etc)."""
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

            if "new_file" in proposal["changes"]:
                rel_path = proposal["changes"]["new_file"]["path"]
                path     = os.path.join(base_dir, rel_path)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                content  = proposal["changes"]["new_file"]["content"]

                # Cek blok otoritas mutlak
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        current = f.read()
                    if "PROTECTED_AUTHORITY_BLOCK" in current:
                        if "PROTECTED_AUTHORITY_BLOCK" not in content:
                            log.critical(f"[EVO] AUTHORITY BREACH BLOCKED: {path}")
                            return False

                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                log.info(f"[EVO] File created/updated: {path}")

            return True
        except Exception as e:
            log.error(f"[EVO] Execution failed: {e}")
            return False


evolution_engine = SovereignEvolutionEngine()



