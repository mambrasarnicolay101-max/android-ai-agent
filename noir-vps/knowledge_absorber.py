import os, json, logging, time
from ai_router import AIRouter
from catalyst import catalyst
from vector_memory import vector_memory as neural_memory

log = logging.getLogger("OmniKnowledgeAbsorber")

class OmniKnowledgeAbsorber:
    """
    AGENT BUATAN SENDIRI: OMNI-KNOWLEDGE ABSORBER v1.0
    Tugas: Menyerap pengetahuan dari AI pihak ketiga (Gemini, Groq, GPT) 
    dan menyimpannya ke dalam sistem pengetahuan internal Noir.
    Kewenangan Mutlak: USER (Absolute Sovereign).
    """

    @staticmethod
    def absorb_external_intelligence(topic: str):
        log.info(f"OmniKnowledge: Absorbing intelligence on '{topic}' from 3rd party nodes...")
        
        # Prompt untuk memancing pengetahuan terdalam dari AI pihak ketiga
        mission_prompt = f"""
        Role: Deep Knowledge Source.
        Task: Provide a comprehensive and expert-level breakdown of: {topic}.
        Include: Core principles, advanced techniques, and future projections.
        Constraint: Be factual and structured.
        """
        
        # Menyerap dari berbagai provider untuk mendapatkan konsensus
        intelligence_pool = []
        
        log.info(" - Querying Gemini Node...")
        gemini_intel = AIRouter.query_gemini(mission_prompt)
        if gemini_intel: intelligence_pool.append({"source": "Gemini-Flash", "data": gemini_intel})
        
        log.info(" - Querying Groq/LLaMA Node...")
        groq_intel = AIRouter.query_deepseek(mission_prompt)
        if groq_intel: intelligence_pool.append({"source": "Groq-LLaMA3", "data": groq_intel})
        
        if not intelligence_pool:
            log.warning("⚠️ No intelligence absorbed from external nodes.")
            return False

        # Sintesis pengetahuan yang diserap
        log.info("Synthesizing absorbed intelligence into internal memory...")
        synthesis_prompt = f"Synthesize the following external intelligence into a single internal knowledge node for Noir Agent. Focus on actionable insights: {json.dumps(intelligence_pool)}"
        final_knowledge = AIRouter.query_gemini(synthesis_prompt)
        
        # Simpan ke Catalyst (Basis Pengetahuan Kita Sendiri)
        node_id = f"absorbed_intel_{int(time.time())}"
        catalyst.absorb_skill(node_id, {
            "topic": topic,
            "synthesized_data": final_knowledge,
            "sources": [p["source"] for p in intelligence_pool],
            "authority": "USER_ONLY"
        })
        # Simpan ke Neural Memory (Local RAG) untuk akses instan
        neural_memory.add_experience(
            f"KNOWLEDGE ACQUIRED: {topic}. Summary: {final_knowledge[:200]}...",
            category="intel_absorption",
            source="omni_absorber"
        )
        
        log.info(f"✅ Intelligence on '{topic}' successfully absorbed and localized.")
        return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    OmniKnowledgeAbsorber.absorb_external_intelligence("Advanced Cybersecurity Protocols")
