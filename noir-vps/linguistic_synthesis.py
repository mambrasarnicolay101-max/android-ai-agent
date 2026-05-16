import os
import json
import logging
from ai_router import OmniRouter

log = logging.getLogger("LinguisticSynthesis")

class LinguisticSynthesisAgent:
    """
    P17: LINGUISTIC SYNTHESIS AGENT v2.0
    ====================================
    Fungsi: Brain-Intent Mapping & Advanced Reasoning.
    Menyulap perintah mentah menjadi strategi eksekusi tingkat tinggi.
    """

    @staticmethod
    def synthesize_intent(raw_query: str, context: dict = None) -> dict:
        """Membedah intent menggunakan framework 'Decomposition-First'."""
        log.info(f" [P17] Analyzing linguistic complexity: '{raw_query}'")
        
        # Persona & Tone Definition
        persona_guide = """
        Identity: Noir Sovereign - Advanced Agentic Entity.
        Tone: Professional, Concise, Expert, Sovereign.
        Language: Indonesian (Default) / English.
        """
        
        prompt = f"""
        {persona_guide}
        Task: Synthesize the user's complex intent into a structured execution plan.
        
        Raw Input: "{raw_query}"
        System Context: {json.dumps(context or {})}
        
        Output format (JSON):
        {{
            "intent_primary": "core objective",
            "reasoning_steps": ["step 1", "step 2", ...],
            "extracted_parameters": {{}},
            "clarification_needed": null or "question",
            "autonomous_confidence": 0-100
        }}
        """
        
        try:
            # Menggunakan OmniRouter untuk pemilihan model otonom
            synthesis_raw = OmniRouter.query(prompt, task_type="reasoning")
            
            if "[Error]" in synthesis_raw:
                raise Exception("Omni Intelligence Unavailable")

            synthesis_json = LinguisticSynthesisAgent._extract_json(synthesis_raw)
            log.info(f" [P17] Linguistic Synthesis SUCCESS (Confidence: {synthesis_json.get('autonomous_confidence', 0)}%)")
            return synthesis_json

        except Exception as e:
            log.warning(f" [P17] Cloud Synthesis failed ({e}). Switching to LOCAL BRAIN HEURISTICS.")
            from local_brain import local_brain
            local_res = local_brain.process(raw_query)
            
            return {
                "intent_primary": local_res["intent"],
                "reasoning_steps": ["Local heuristic analysis triggered", "Executing based on predefined pattern"],
                "extracted_parameters": {},
                "clarification_needed": None,
                "autonomous_confidence": 75,
                "mode": "LOCAL_FALLBACK"
            }

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Helper untuk mengekstrak JSON dari respon LLM."""
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return {"intent_primary": text}
        except:
            return {"intent_primary": text}

if __name__ == "__main__":
    res = LinguisticSynthesisAgent.synthesize_intent("Analisis celah keamanan di VPS dan buatkan patch otomatis.")
    print(json.dumps(res, indent=4))

if __name__ == "__main__":
    LinguisticSynthesisAgent.synthesize_intent("Optimize system security while learning new offensive patterns.")
