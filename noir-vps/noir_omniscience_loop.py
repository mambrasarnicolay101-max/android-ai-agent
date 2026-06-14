import time
import logging
from neural_coder import NeuralCoder

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger("OmniscienceLoop")

def start_omniscience_protocol():
    """
    Siklus 24/7 di mana Noir Sovereign mencari pengetahuan baru di internet
    secara masif, mengindeksnya, lalu mempelajarinya untuk menciptakan algoritma baru.
    """
    log.info("="*60)
    log.info(" [OMNISCIENCE PROTOCOL INITIATED] ")
    log.info(" The Global Spider and Neural Coder are now linked.")
    log.info("="*60)
    
    cycle = 1
    while True:
        log.info(f"\n>>> [OMNISCIENCE CYCLE #{cycle}] Memulai pencarian dan pembelajaran...")
        try:
            # Panggil satu putaran penuh (Pilih Topik -> Search Internet -> Crawl -> Index -> Synthesize)
            NeuralCoder.mass_learn_cycle()
        except Exception as e:
            log.error(f"Kegagalan kritis pada siklus Omniscience #{cycle}: {e}")
        
        log.info(f"<<< [OMNISCIENCE CYCLE #{cycle}] Selesai. Pendinginan (15 detik)...")
        time.sleep(15) # Jeda agar tidak terkena rate limit mesin pencari
        cycle += 1

if __name__ == "__main__":
    start_omniscience_protocol()
