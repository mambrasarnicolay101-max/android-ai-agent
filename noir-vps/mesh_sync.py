import os
import json
import logging
import requests
import time

log = logging.getLogger("SovereignMesh")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [MESH] %(message)s")

class SovereignMesh:
    """
    Sovereign Mesh v1.0  Multi-Node Synchronization
    ===============================================
    Sinkronisasi pengetahuan, skill, dan security patches antar node (VPS, Mobile, PC).
    Memastikan "Kekebalan Kolektif" di seluruh ekosistem Noir Sovereign.
    """
    GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")).rstrip("/")
    API_KEY = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
    HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    @staticmethod
    def broadcast_knowledge(title, content, sync_type="skill"):
        """Mengirimkan pengetahuan baru ke seluruh node yang terhubung."""
        log.info(f"[SYNC] Memancarkan pengetahuan: {title} (Type: {sync_type})")
        
        # Payload untuk dikirim ke Mobile Agent / PC Agent
        payload = {
            "target_device": "ALL_NODES", # Broadcast mode
            "action": {
                "type": "mesh_sync_push",
                "params": {
                    "title": title,
                    "payload": content,
                    "sync_type": sync_type,
                    "origin": "VPS_MASTER"
                }
            },
            "description": f"Mesh Knowledge Sync: {title}",
            "priority": 2
        }

        try:
            # Kirim ke Gateway (Gateway akan meneruskan ke agen via poll/websocket)
            resp = requests.post(f"{SovereignMesh.GATEWAY}/api/command", json=payload, headers=SovereignMesh.HEADERS, timeout=10)
            if resp.status_code == 200:
                log.info(f"[SUCCESS] Pengetahuan berhasil dipancarkan ke jalur Mesh.")
                return True
        except Exception as e:
            log.error(f"[ERROR] Gagal memancarkan ke Mesh: {e}")
        return False

    @staticmethod
    def run_full_sync():
        """Sinkronisasi total riwayat evolusi terbaru."""
        log.info("[MESH] Memulai sinkronisasi total ekosistem...")
        history_file = os.path.join(os.path.dirname(__file__), "..", "knowledge", "evolution", "evolution_history.json")
        if not os.path.exists(history_file):
            log.warning("Tidak ada riwayat evolusi untuk disinkronkan.")
            return
            
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            if not history: return

            # Kirim evolusi terbaru (max 5)
            latest = history[-5:]
            for item in latest:
                SovereignMesh.broadcast_knowledge(
                    title=item.get("title"),
                    content=item.get("changes"),
                    sync_type="evolution_update"
                )
                time.sleep(1) # Gap agar tidak membebani gateway
            
            log.info("[MESH] Sinkronisasi ekosistem selesai.")
        except Exception as e:
            log.error(f"[MESH] Gagal menjalankan sinkronisasi: {e}")

if __name__ == "__main__":
    SovereignMesh.run_full_sync()
