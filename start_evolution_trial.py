import sys, os, logging
sys.path.append(os.path.join(os.path.dirname(__file__), "noir-vps"))

from brain import SelfEvolutionEngine
from knowledge_absorber import OmniKnowledgeAbsorber
from neural_architect import NeuralArchitect
from ai_router import AIRouter
from red_blue_arena import RedBlueArena

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("EvolutionTrial")

def run_trial():
    log.info("==================================================")
    log.info("STARTING SOVEREIGN SELF-EVOLUTION TRIAL...")
    log.info("==================================================")
    
    # 1. Absorbs Knowledge from external sources
    topic = "Advanced Local AI Inference optimization for Python 3.11"
    log.info(f"Phase 1: Absorbing knowledge on {topic}...")
    OmniKnowledgeAbsorber.absorb_external_intelligence(topic)
    
    # 2. Autonomous discovery of a new tech trend
    log.info("Phase 2: Running Autonomous Discovery...")
    SelfEvolutionEngine.run_daily_discovery()
    
    # 3. Architect audit based on new knowledge
    log.info("Phase 3: Triggering Neural Architect Audit...")
    NeuralArchitect.self_audit_and_design()
    
    # 4. Red-Blue Simulation Arena
    log.info("Phase 4: Entering Red-Blue Security Training Arena...")
    arena = RedBlueArena()
    arena.run_simulation()
    
    log.info("==================================================")
    log.info("SELF-EVOLUTION TRIAL COMPLETED.")
    log.info("Check Dashboard 'EVOLUTION' and 'MEM' chips for progress.")
    log.info("==================================================")

if __name__ == "__main__":
    run_trial()

