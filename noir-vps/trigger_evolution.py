"""
APEX EVOLUTION CYCLE TRIGGER
Triggers the P24 Apex Evolution Engine cycle to synthesize the first APEX skill.
"""
import sys, os, logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("TriggerEvolution")

# Add paths
sys.path.append(os.path.dirname(__file__))
from apex_evolution import ApexEvolutionEngine

try:
    log.info("Memulai pemicu evolusi otonom P24...")
    result = ApexEvolutionEngine.run_recursive_evolution_cycle()
    log.info("═══ SIKLUS EVOLUSI SUKSES ═══")
    print(f"Skill Baru Disintesis: {result.get('skill_name', 'N/A')}")
    print(f"Domain Terpilih: {result.get('domain', 'N/A')} / {result.get('sub_domain', 'N/A')}")
except Exception as e:
    log.error(f"Gagal memicu siklus evolusi: {e}")
    import traceback
    traceback.print_exc()
