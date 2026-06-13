import time
import logging
import threading
from grand_singularity_cycle import GrandSingularityCycle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("../knowledge/singularity_daemon.log", encoding="utf-8"),
    ]
)
log = logging.getLogger("SingularityDaemon")

# ── Grand Evolution Loop (background) ─────────────────────────────────────────
def _start_evolution_loop():
    """Jalankan Grand Evolution Loop di thread terpisah."""
    try:
        from noir_grand_evolution_loop import start_loop_background
        start_loop_background()
        log.info("[DAEMON] Grand Evolution Loop berhasil dimulai di background.")
    except Exception as e:
        log.warning(f"[DAEMON] Grand Evolution Loop tidak dapat dimulai: {e}")

def start_daemon(interval_minutes=5):
    """
    Menjalankan Grand Singularity Cycle secara terus-menerus.
    Jeda diberikan agar tidak membebani limit API (terutama versi free-tier).
    Grand Evolution Loop berjalan paralel di thread terpisah.
    """
    log.info(f"=== SOVEREIGN SINGULARITY DAEMON V33.0 STARTED ===")
    log.info(f"Interval antar siklus: {interval_minutes} menit")

    # Mulai Grand Evolution Loop di background (non-blocking)
    evo_thread = threading.Thread(target=_start_evolution_loop, daemon=True)
    evo_thread.start()

    engine = GrandSingularityCycle()

    while True:
        try:
            engine.run_cycle()
        except Exception as e:
            log.error(f"Siklus Singularitas gagal karena error: {e}")
            log.info("Mencoba ulang pada siklus berikutnya...")

        # Hibernasi sebelum siklus berikutnya
        sleep_seconds = interval_minutes * 60
        log.info(f"=== Menunggu {interval_minutes} menit sebelum siklus berikutnya ===")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    start_daemon(interval_minutes=5)
