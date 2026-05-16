import os, sys, time, logging
sys.path.append(os.path.abspath("noir-vps"))

from red_blue_arena import RedBlueArena
from sovereign_orchestrator import spawn_sub_agent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [BRUTAL_WARFARE] %(message)s")
log = logging.getLogger("BrutalWarfare")

def run_brutal_warfare_cycle():
    arena = RedBlueArena()
    log.info("!!! INITIATING MASSIVE & BRUTAL WARFARE CYCLE !!!")
    
    # Run 5 simulations in parallel via sub-agents
    for i in range(5):
        spawn_sub_agent(f"Warfare_Node_{i}", arena.run_simulation, "BRUTAL")
        time.sleep(2) # Stagger slightly to avoid API flooding
    
    log.info("5 Parallel Warfare Nodes SPAWNED. System is now in a state of continuous evolution.")

if __name__ == "__main__":
    run_brutal_warfare_cycle()
