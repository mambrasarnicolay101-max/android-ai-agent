import multiprocessing
import time
import logging
from live_combat_loop import LiveCombatEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [HYDRA] %(message)s")
log = logging.getLogger("HydraSwarm")

def spawn_hydra_head(head_id, target="http://127.0.0.1:8080/"):
    log.info(f"Membangkitkan Kepala Hydra #{head_id} menargetkan {target}")
    combat_bot = LiveCombatEngine(target_url=target)
    
    # Bypass infinite loop untuk simulasi hydra agar tidak membebani PC
    # Dalam produksi, ini bisa berupa loop while True
    for cycle in range(1, 4):
        log.info(f"[Hydra #{head_id}] Siklus Serangan {cycle}/3")
        try:
            vector = combat_bot.generate_attack_vector()
            combat_bot.execute_on_vps(vector)
            time.sleep(2) # Hindari rate limiting Llama-3 API
        except Exception as e:
            log.error(f"[Hydra #{head_id}] Error: {e}")

def unleash_the_swarm(num_heads=5, target="http://127.0.0.1:8080/"):
    log.critical(f"!!! MELEPASKAN HYDRA SWARM ({num_heads} KEPALA) !!!")
    log.critical(f"Target Utama: {target}")
    
    processes = []
    for i in range(num_heads):
        p = multiprocessing.Process(target=spawn_hydra_head, args=(i+1, target))
        processes.append(p)
        p.start()
        time.sleep(1) # Stagger start times
        
    for p in processes:
        p.join()
        
    log.info("Seluruh Kepala Hydra telah ditarik kembali. Siklus Swarm Selesai.")

if __name__ == "__main__":
    # Target difokuskan ke Local Arena (127.0.0.1) untuk mencegah ban VPS
    unleash_the_swarm(num_heads=3)
