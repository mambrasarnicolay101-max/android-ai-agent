import os, json, logging, re
from ai_router import OmniRouter

log = logging.getLogger("NLUProcessor")

class NLUProcessor:
    """Mesin Pemrosesan Bahasa Alami untuk menormalisasi dan mengekstrak intent."""
    
    @staticmethod
    def normalize_input(text: str) -> dict:
        """Menormalisasi input dengan pendekatan hybrid (Local Mapping + AI)."""
        raw_text = text.lower().strip()
        
        # 1. LOCAL FAST-MAPPING (Enhanced v17.0)
        local_mapping = {
            "ss": "TAKE_SCREENSHOT", "screenshot": "TAKE_SCREENSHOT", "foto": "TAKE_SCREENSHOT", "layar": "TAKE_SCREENSHOT",
            "baterai": "GET_BATTERY", "batere": "GET_BATTERY", "battery": "GET_BATTERY", "persen": "GET_BATTERY",
            "info": "GET_STATUS", "status": "GET_STATUS", "noir": "GET_STATUS", "kondisi": "GET_STATUS",
            "reboot": "SYSTEM_ACTION", "restart": "SYSTEM_ACTION", "matikan": "SYSTEM_ACTION", "hidupkan": "SYSTEM_ACTION",
            "wifi": "WIFI_TOGGLE", "data": "DATA_TOGGLE", "bluetooth": "BT_TOGGLE",
            "audit": "RUN_AUDIT", "periksa": "RUN_AUDIT", "cek": "RUN_AUDIT",
            "upgrade": "SYSTEM_UPGRADE", "update": "SYSTEM_UPGRADE", "perbarui": "SYSTEM_UPGRADE"
        }
        
        for key, intent in local_mapping.items():
            if key in raw_text:
                log.info(f" NLU: Local Match Found -> {intent}")
                return {
                    "original": text,
                    "normalized": raw_text,
                    "intent": intent,
                    "entities": {},
                    "slang_detected": True
                }

        # 2. AI SMART NORMALIZATION (Re-enabled for Elite v17)
        try:
            prompt = f"Identify the intent of this message for an Android AI Agent. Return only the intent code (e.g. TAKE_SCREENSHOT, GET_BATTERY, SYSTEM_ACTION, RUN_AUDIT, or UNKNOWN). Message: '{raw_text}'"
            intent = OmniRouter.query_gemini(prompt).strip().upper()
            if intent != "UNKNOWN":
                return {"original": text, "normalized": raw_text, "intent": intent, "entities": {}, "slang_detected": False}
        except: pass

        return {"original": text, "normalized": text, "intent": "UNKNOWN", "entities": {}, "slang_detected": False}

    @staticmethod
    def extract_pattern(normalized_text: str):
        """Mengekstrak pola struktur kalimat untuk pembelajaran otonom."""
        # Contoh: "Tolong nyalakan lampu" -> "ACTION_REQUEST(verb=nyalakan, target=lampu)"
        prompt = f"Analyze the grammatical structure of this normalized sentence and return a pattern template: '{normalized_text}'"
        pattern = OmniRouter.query_gemini(prompt)
        return pattern
