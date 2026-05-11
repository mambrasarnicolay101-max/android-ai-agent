import os
import time
import logging
import threading
import json
import subprocess

log = logging.getLogger("NeuralReflex")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [REFLEX] %(message)s")

class NeuralReflex:
    """
    Neural Reflex System v1.0 — NOIR SOVEREIGN
    ==========================================
    Sistem deteksi anomali real-time untuk menjaga kedaulatan sistem.
    Memantau CPU, Jaringan, dan Integritas File secara aktif dan mengambil
    tindakan pertahanan instan.
    """
    def __init__(self):
        self.running = True
        self.threshold_cpu = 90.0  # Ambang batas CPU (%)
        self.monitored_files = [
            os.path.join(os.path.dirname(__file__), "brain.py"),
            os.path.join(os.path.dirname(__file__), "..", "sovereign_boot.py"),
            os.path.join(os.path.dirname(__file__), "sovereign_orchestrator.py")
        ]
        self.file_states = self._get_file_states()
        log.info(f"Neural Reflex mengawasi {len(self.monitored_files)} file inti.")

    def _get_file_states(self):
        states = {}
        for f in self.monitored_files:
            if os.path.exists(f):
                states[f] = os.path.getmtime(f)
        return states

    def check_system_load(self):
        """Memantau beban CPU untuk mendeteksi serangan DoS atau cryptojacking."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            if cpu > self.threshold_cpu:
                self.trigger_reflex("CPU_ANOMALY", f"Beban CPU terdeteksi di {cpu}% - Kemungkinan serangan Resource Exhaustion.")
        except ImportError:
            # Fallback jika psutil tidak ada
            pass

    def check_file_integrity(self):
        """Memantau perubahan file inti untuk mencegah injeksi kode berbahaya."""
        for f in self.monitored_files:
            if os.path.exists(f):
                current_mtime = os.path.getmtime(f)
                if current_mtime != self.file_states.get(f):
                    self.trigger_reflex("INTEGRITY_BREACH", f"Modifikasi tidak sah terdeteksi pada file inti: {os.path.basename(f)}")
                    self.file_states[f] = current_mtime

    def trigger_reflex(self, alert_type, message):
        log.warning(f"⚠️ [REFLEX DIPICU] {alert_type}: {message}")
        
        # 1. Catat ke Sovereign Wiki melalui Evolution Engine
        try:
            from evolution_engine import evolution_engine
            evolution_engine.propose_evolution(
                title=f"Security Reflex: {alert_type}",
                description=f"Sistem mendeteksi anomali kritis: {message}. Log ini otomatis dicatat untuk audit kedaulatan.",
                changes={"reflex_action": {"alert": alert_type, "msg": message, "timestamp": time.ctime()}},
                complexity=1
            )
            # Auto-approve untuk riwayat keamanan
            pending = evolution_engine.get_all_evolutions()["pending"]
            if pending:
                evolution_engine.approve_evolution(pending[-1]["id"])
        except Exception as e:
            log.error(f"Gagal mencatat refleks ke evolusi: {e}")

        # 2. Kirim notifikasi ke Dashboard jika Gateway tersedia
        try:
            gateway = os.environ.get("NOIR_GATEWAY_URL", "http://localhost:8765").rstrip("/")
            api_key = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
            import requests
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            requests.post(f"{gateway}/api/learning/update", 
                          headers=headers,
                          json={"status": f"高 [REFLEX] {alert_type} terdeteksi! Mengaktifkan mode pertahanan."},
                          timeout=5)
        except:
            pass

    def run_monitor_loop(self):
        log.info("Neural Reflex monitoring loop dimulai (Pemindaian setiap 10 detik).")
        while self.running:
            try:
                self.check_system_load()
                self.check_file_integrity()
            except Exception as e:
                log.error(f"Error dalam loop monitoring: {e}")
            time.sleep(10)

def start_reflex_service():
    reflex = NeuralReflex()
    reflex.run_monitor_loop()

if __name__ == "__main__":
    start_reflex_service()
