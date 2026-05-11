import os
import json
import time
import requests
import logging
import zipfile

log = logging.getLogger("ShadowNode")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [SHADOW] %(message)s")

class ShadowNode:
    """
    Shadow Node v1.0 — Failover & High Availability
    =============================================
    Mengelola node cadangan untuk memastikan kedaulatan AI tetap aktif
    meskipun node utama mengalami gangguan.
    """
    
    # Konfigurasi Node (Bisa disesuaikan oleh user di .env)
    PRIMARY_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
    SHADOW_IP = os.environ.get("NOIR_SHADOW_IP", "0.0.0.0") # Target node cadangan
    
    STATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))
    BACKUP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".sandbox", "shadow_state.zip"))

    @staticmethod
    def create_state_snapshot():
        """Mengemas seluruh 'kesadaran' (knowledge folder) menjadi snapshot."""
        log.info("[SHADOW] Membuat snapshot kesadaran (State Snapshot)...")
        try:
            os.makedirs(os.path.dirname(ShadowNode.BACKUP_PATH), exist_ok=True)
            with zipfile.ZipFile(ShadowNode.BACKUP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(ShadowNode.STATE_DIR):
                    for file in files:
                        zipf.write(os.path.join(root, file), 
                                   os.path.relpath(os.path.join(root, file), 
                                   os.path.join(ShadowNode.STATE_DIR, '..')))
            log.info(f"[SHADOW] Snapshot berhasil dibuat: {ShadowNode.BACKUP_PATH}")
            return True
        except Exception as e:
            log.error(f"[SHADOW] Gagal membuat snapshot: {e}")
            return False

    @staticmethod
    def check_node_health(ip):
        """Memeriksa kesehatan node lain via health endpoint."""
        if ip == "0.0.0.0": return False
        try:
            resp = requests.get(f"http://{ip}:8765/health", timeout=5)
            if resp.status_code == 200:
                return True
        except:
            pass
        return False

    @staticmethod
    def run_heartbeat_cycle():
        """Siklus pemantauan detak jantung (Heartbeat)."""
        log.info(f"[SHADOW] Memulai siklus detak jantung. Primary: {ShadowNode.PRIMARY_IP}")
        
        # Jika ini adalah Primary, kita buat snapshot untuk siap dikirim
        ShadowNode.create_state_snapshot()
        
        # Simulasi deteksi Shadow Node
        if ShadowNode.SHADOW_IP != "0.0.0.0":
            is_alive = ShadowNode.check_node_health(ShadowNode.SHADOW_IP)
            status = "ONLINE" if is_alive else "OFFLINE"
            log.info(f"[SHADOW] Shadow Node ({ShadowNode.SHADOW_IP}) status: {status}")
            
            # Jika Shadow Online, kita kirim snapshot (Simulasi Sync)
            if is_alive:
                log.info("[SHADOW] Mensinkronkan state ke Shadow Node...")
        else:
            log.info("[SHADOW] Shadow Node belum dikonfigurasi. Menunggu Node cadangan...")

if __name__ == "__main__":
    ShadowNode.run_heartbeat_cycle()
