import os, sys, time, logging, json
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(__file__))
from ai_router import OmniRouter
from vector_memory import vector_memory
from evolution_engine import evolution_engine
from red_blue_arena import RedBlueArena

log = logging.getLogger("GrandSingularity")

class GrandSingularityCycle:
    """
    GRAND SINGULARITY CYCLE v1.0
    ============================
    Orkestrator kecerdasan tingkat tinggi untuk evolusi otonom 24/7.
    Mengelola siklus berpikir, belajar, simulasi, dan perbaikan diri.
    """

    def __init__(self):
        self.arena = RedBlueArena()
        self.last_rem_sleep = time.time()
        self.state_file = os.path.join(os.path.dirname(__file__), "..", "knowledge", "singularity_state.json")
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except: pass
        return {"cycle": 0, "total_evolutions": 0}

    def _save_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save singularity state: {e}")

    def run_cycle(self):
        """Menjalankan satu siklus penuh evolusi otonom."""
        self.state["cycle"] += 1
        log.info(f" [SINGULARITY] Starting Grand Evolution Cycle #{self.state['cycle']}...")
        
        # 1. RESEARCH & KNOWLEDGE ABSORPTION
        self._step_research()
        
        # 2. SIMULATION & WARFARE TRAINING
        self._step_simulation()
        
        # 3. SELF-AUDIT & HARDENING
        self._step_self_audit()
        
        # 4. REM SLEEP (MEMORY CONSOLIDATION)
        if time.time() - self.last_rem_sleep > 43200: # Every 12 hours
            self._step_rem_sleep()
            self.last_rem_sleep = time.time()

        self._save_state()
        log.info(f" [SINGULARITY] Cycle #{self.state['cycle']} completed. Sleeping until next window.")

    def _step_research(self):
        """Tahap Penelitian: AI mencari tren keamanan dan teknologi baru."""
        log.info(" [SINGULARITY] Phase 1: Autonomous Research...")
        topics = [
            "LLM Security Vulnerabilities 2026",
            "Advanced Evasion Techniques for Android Sandboxes",
            "Post-Quantum Cryptography in Python",
            "Zero-Day Analysis Methodology"
        ]
        import random
        topic = random.choice(topics)
        
        prompt = f"Research the latest information about '{topic}'. Summarize key techniques and provide a Python snippet if applicable for defense or testing."
        research_result = OmniRouter.query(prompt, task_type="reasoning")
        
        if research_result and "[Error]" not in research_result:
            vector_memory.add_experience(
                text=f"Research on {topic}: {research_result}",
                metadata={"source": "grand_singularity", "type": "research_insight", "topic": topic}
            )
            log.info(f" [SINGULARITY] Research on '{topic}' assimilated into memory.")

    def _step_simulation(self):
        """Tahap Simulasi: Red vs Blue Arena dengan peningkatan LLM."""
        log.info(" [SINGULARITY] Phase 2: Cyber Warfare Simulation...")
        try:
            self.arena.run_simulation()
            log.info(" [SINGULARITY] Simulation Arena cycle finished.")
        except Exception as e:
            log.error(f" [SINGULARITY] Simulation failed: {e}")

    def _step_self_audit(self):
        """Tahap Audit Mandiri: Mencari anti-pattern dalam kode sendiri."""
        log.info(" [SINGULARITY] Phase 3: Recursive Self-Audit...")
        # Pilih file acak untuk di-audit
        core_files = ["brain.py", "ai_router.py", "sovereign_orchestrator.py", "web_server.py"]
        import random
        target = random.choice(core_files)
        target_path = os.path.join(os.path.dirname(__file__), target) if target != "web_server.py" else os.path.join(os.path.dirname(__file__), "..", "noir-ui", target)
        
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                code = f.read()
            
            prompt = f"Perform a security and performance audit on the following code. Identify potential bugs, race conditions, or security holes. Code:\n\n{code[:4000]}"
            audit_report = OmniRouter.query(prompt, task_type="coding")
            
            if audit_report and "[Error]" not in audit_report:
                evolution_engine.propose_evolution(
                    title=f"AI Self-Audit Result: {target}",
                    description=f"Automated audit findings for {target}:\n\n{audit_report}",
                    changes={"audit_findings": {"file": target, "report": audit_report}},
                    complexity=3
                )
                log.info(f" [SINGULARITY] Audit for '{target}' completed. Proposals sent to Evolution Engine.")

    def _step_rem_sleep(self):
        """Tahap REM Sleep: Mengonsolidasi memori dan menyaring pengetahuan berharga."""
        log.info(" [SINGULARITY] Phase 4: REM Sleep (Memory Consolidation)...")
        # Ambil memori terakhir dan ringkas
        memories = vector_memory.query("recent events", n_results=10)
        if memories:
            summary_prompt = f"Summarize these recent experiences into 'Core Beliefs' for the AI system. What has been learned? Memories:\n\n" + "\n".join(memories)
            summary = OmniRouter.query(summary_prompt, task_type="reasoning")
            
            if summary and "[Error]" not in summary:
                vector_memory.add_experience(
                    text=f"Core Belief Consolidation: {summary}",
                    metadata={"source": "rem_sleep", "type": "core_belief"}
                )
                log.info(" [SINGULARITY] Memory consolidation successful.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = GrandSingularityCycle()
    engine.run_cycle()
