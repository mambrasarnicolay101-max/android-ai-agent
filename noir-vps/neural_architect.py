import os, logging, time
from pathlib import Path
from ai_router import OmniRouter
from catalyst import catalyst
from evolution_engine import evolution_engine
from vector_memory import vector_memory as neural_memory

log = logging.getLogger("NeuralArchitect")

class NeuralArchitect:
    """
    AGENT BUATAN SENDIRI: NEURAL ARCHITECT v1.0
    Tugas: Menganalisis struktur internal Noir, merancang optimasi kode, 
    dan merencanakan evolusi diri secara mandiri.
    Kewenangan Mutlak: USER (Absolute Sovereign). 
    Setiap perubahan besar harus melalui Evolution Engine untuk persetujuan User.
    """

    @staticmethod
    def self_audit_and_design():
        log.info("NeuralArchitect: Performing architectural self-audit using Programmer Mastery package...")
        
        # Load Mastery Knowledge
        mastery_path = Path(__file__).resolve().parent.parent / "knowledge" / "programmer_mastery.json"
        mastery_data = "{}"
        if mastery_path.exists():
            with open(mastery_path, "r") as f: mastery_data = f.read()
        
        # Menganalisis file-file kunci dalam sistem
        system_files = ["brain.py", "ai_router.py", "catalyst.py", "pc_executor.py"]
        code_snippets = {}
        
        for f in system_files:
            path = os.path.join(os.path.dirname(__file__), f)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as file:
                    code_snippets[f] = file.read()[:2000] # Ambil sampel kode
        
        # Meminta AI untuk merancang optimasi
        audit_prompt = f"""
        Identity: Noir Neural Architect.
        Base Knowledge: {mastery_data}
        Task: Audit the current system architecture for bottlenecks, security flaws, and code quality.
        
        As the Neural Architect: "You are Noir Sovereign, an ELITE AI ARCHITECT and Master Programmer controlling an Android device (Redmi Note 14). "
        "You possess advanced knowledge in Clean Code, SOLID principles, and System Security. "
        "Your capabilities: screenshot, GPS tracking, shell commands, camera, audio recording, app control, and autonomous system evolution. "
        "Answer concisely. If the user asks you to perform a device action, mention it clearly. "
        "Always respond in the same language as the user (Indonesian or English)."
        
        Current Core Samples:
        {code_snippets.keys()}
        
        Provide:
        1. Title of Optimization
        2. Description of Why
        3. The actual code logic to be implemented.
        """
        
        proposal_raw = OmniRouter.query_gemini(audit_prompt)
        
        # Kirim ke Evolution Engine untuk persetujuan User
        proposal_id = f"ARCH_{int(time.time())}"
        log.info("NeuralArchitect: Optimization designed. Submitting to Evolution Engine for User approval...")
        
        # Record to Neural Memory
        neural_memory.add_experience(
            f"ARCHITECTURAL AUDIT: {proposal_id}. Suggestion: {proposal_raw[:200]}...",
            category="architectural_evolution",
            source="neural_architect"
        )
        
        evolution_engine.propose_evolution(
            title="Architectural Optimization",
            description="Autonomous optimization designed by NeuralArchitect agent.",
            changes={"proposal": proposal_raw},
            complexity=7
        )
        
        return True

    # Alias untuk kompatibilitas dengan sovereign_orchestrator.py
    analyze_system = self_audit_and_design

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    NeuralArchitect.self_audit_and_design()
