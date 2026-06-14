import logging
import time
from .noir_system_architect import SystemArchitect
from .offensive_predator import OffensivePredator
from .sovereign_defense import SovereignDefense

log = logging.getLogger("TrinityLoop")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class TrinityLoop:
    """
    [THE SOVEREIGN TRINITY]
    Siklus inti yang menggabungkan:
    1. The Builder (Membangun Web/APK/EXE otonom)
    2. The Offense (Mencari celah keamanan & penyerangan)
    3. The Defense (Membangun honeypot & self-healing)
    """

    def __init__(self):
        self.builder = SystemArchitect()
        self.offense = OffensivePredator()
        self.defense = SovereignDefense()
        log.info("[Trinity] The Sovereign Trinity telah diinisialisasi. Tiga pilar aktif.")

    def run_cycle(self):
        """Menjalankan satu iterasi penuh dari The Trinity"""
        log.info("\n" + "="*50)
        log.info("[TRINITY] MEMULAI SIKLUS EVOLUSI BARU")
        log.info("="*50)

        # 1. THE DEFENSE (Membangun Perlindungan)
        log.info("\n--- [PILAR 1: DEFENSE] ---")
        try:
            # Meminta builder untuk membuat fake service/honeypot berbasis Web
            log.info("[Trinity] Memerintahkan Builder menciptakan Web Honeypot...")
            self.builder.autonomous_create("A realistic-looking login portal for internal admin to trap hackers", "web")
            # Eksekusi scan pertahanan
            self.defense.scan_host()
        except Exception as e:
            log.error(f"[Trinity] Defense error: {e}")

        # 2. THE OFFENSE (Mencari Target)
        log.info("\n--- [PILAR 2: OFFENSE] ---")
        try:
            # Meminta builder untuk membuat payload dropper
            log.info("[Trinity] Memerintahkan Builder menciptakan EXE Dropper Payload...")
            self.builder.autonomous_create("A silent background process that logs basic system info and connects back", "exe")
            # Eksekusi pencarian target
            target = self.offense.hunt()
            if target:
                log.info(f"[Trinity] Target ditemukan: {target}")
        except Exception as e:
            log.error(f"[Trinity] Offense error: {e}")

        # 3. THE BUILDER (Inovasi & Evolusi)
        log.info("\n--- [PILAR 3: BUILDER] ---")
        try:
            log.info("[Trinity] Membangun aset internal secara otonom...")
            # Membuat GUI Android APK untuk kontrol panel Noir
            self.builder.autonomous_create("A Flet-based Android App UI for monitoring system status and showing server metrics", "apk")
        except Exception as e:
            log.error(f"[Trinity] Builder error: {e}")

        log.info("\n[TRINITY] Siklus Selesai. Menunggu iterasi berikutnya...\n")

if __name__ == "__main__":
    loop = TrinityLoop()
    # Untuk uji coba, kita jalankan 1 siklus saja
    loop.run_cycle()
