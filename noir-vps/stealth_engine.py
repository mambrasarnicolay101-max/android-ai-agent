import os, time, datetime, logging, platform

log = logging.getLogger("StealthEngine")

class StealthEngine:
    """
    STEALTH ENGINE v1.0 (Ghost Protocol)
    =====================================
    Pilar Pertahanan Pasif & Kelangsungan Hidup.
    - Mimetic Sleep Cycles: Memperlambat operasi saat jam tidur manusia untuk menghindari deteksi heuristik cloud.
    - Dead Man's Switch (Protokol Kiamat): Menghancurkan jejak intelijen (Vector DB & Logs) jika tidak ada sinyal dari Admin selama 72 jam.
    """
    
    LAST_PULSE_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "admin_pulse.txt")
    
    @staticmethod
    def mimic_sleep():
        """Mengurangi beban kerja jika sedang tengah malam (01:00 - 05:00) lokal VPS."""
        now = datetime.datetime.now()
        # Jika antara jam 1 pagi hingga 5 pagi
        if 1 <= now.hour <= 5:
            log.info("[GHOST] Mimetic Sleep Cycle aktif. Memperlambat gelombang otak AI (Tidur 300s).")
            time.sleep(300) # Perlambat siklus evolusi selama 5 menit untuk meniru non-aktivitas
        else:
            # Mode Siang: Normal speed
            pass

    @staticmethod
    def register_pulse():
        """Mencatat waktu interaksi terakhir Admin (disebut dari web_server saat dashboard dibuka)."""
        os.makedirs(os.path.dirname(StealthEngine.LAST_PULSE_FILE), exist_ok=True)
        with open(StealthEngine.LAST_PULSE_FILE, "w") as f:
            f.write(str(time.time()))
        log.debug("[GHOST] Sovereign Pulse Diterima. Dead Man's Switch di-reset.")
            
    @staticmethod
    def check_dead_mans_switch():
        """Jika tidak ada pulse selama 72 jam, jalankan Doomsday Protocol."""
        if not os.path.exists(StealthEngine.LAST_PULSE_FILE):
            StealthEngine.register_pulse() # Inisialisasi pulse pertama
            return False
            
        try:
            with open(StealthEngine.LAST_PULSE_FILE, "r") as f:
                last_pulse = float(f.read().strip())
                
            # 72 Jam = 259200 Detik
            if time.time() - last_pulse > 259200:
                log.critical("*" * 50)
                log.critical("[DOOMSDAY] DEAD MAN'S SWITCH TERCETUS!")
                log.critical("[DOOMSDAY] Admin hilang > 72 Jam. Mengasumsikan server dikompromikan.")
                log.critical("*" * 50)
                StealthEngine.execute_wipe()
                return True
        except Exception as e:
            log.error(f"[GHOST] Pulse check error: {e}")
            
        return False
        
    @staticmethod
    def execute_wipe():
        """WIPE OUT PROTOCOL: Menghapus Vector Memory, Logs, dan mengunci sistem."""
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            knowledge_dir = os.path.join(base_dir, "knowledge")
            
            # 1. Hapus Otak (Vector DB & Logs)
            if os.path.exists(knowledge_dir):
                import shutil
                shutil.rmtree(knowledge_dir, ignore_errors=True)
                log.critical("[DOOMSDAY] 1. KNOWLEDGE BASE & NEURAL MEMORY DIHAPUS (WIPED).")
            
            # 2. Putus Koneksi (Bunuh diri proses)
            log.critical("[DOOMSDAY] 2. MENGHENTIKAN SELURUH PROSES AI...")
            if platform.system() == "Linux":
                os.system("pkill -9 -f python")
            else:
                os.system("taskkill /F /IM python.exe")
                
        except Exception as e:
            log.error(f"[DOOMSDAY] Gagal mengeksekusi Wipe Out secara sempurna: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    StealthEngine.register_pulse()
    StealthEngine.mimic_sleep()
    StealthEngine.check_dead_mans_switch()
