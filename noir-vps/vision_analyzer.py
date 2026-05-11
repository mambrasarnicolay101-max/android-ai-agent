import os, json, logging
import base64
import cv2
import numpy as np
from ai_router import AIRouter
from catalyst import catalyst
from temporal_memory import global_memory as memory

from datetime import datetime

log = logging.getLogger("VisionAnalyzer")

class ScreenVisionIntelligence:
    """Modul AI baru untuk menganalisis konteks layar secara visual."""
    
    @staticmethod
    def analyze_screen(image_path: str):
        log.info("👁️ Vision Intelligence: Analyzing current screen state...")
        
        if not os.path.exists(image_path):
            return {"error": "Screen image not found."}
            
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
            prompt = """
            Analyze this Android screenshot. Identify:
            1. What app is currently open?
            2. Are there any sensitive elements (passwords, banking interfaces)?
            3. What is the overall context of the screen?
            
            Return ONLY a valid JSON:
            {
                "app_detected": "App Name",
                "is_sensitive": true/false,
                "context": "Short description of what is happening"
            }
            """
            
            # Memanfaatkan kemampuan multimodal & native JSON Gemini 2.0 Flash
            response = AIRouter.query_gemini(prompt, image_base64=encoded_string, response_json=True)
            result = json.loads(response)
            
            # FASE 3: Deteksi UI Elements
            ui_elements = ScreenVisionIntelligence.extract_ui_elements(image_path)
            result["ui_elements_count"] = len(ui_elements)
            result["ui_elements"] = ui_elements

            # 4. Integrate into Catalyst Knowledge
            catalyst.absorb_skill("Vision_Screen_Analysis", {"app": result.get("app_detected"), "complexity": 3})
            
            # --- NEW: Temporal Memory Storage ---
            ScreenVisionIntelligence.save_to_memory(result)
            
            return result
        except Exception as e:
            log.error(f"Vision Analysis Failed: {e}")
            return {"error": str(e)}

    @staticmethod
    def save_to_memory(analysis: dict):
        """Menyimpan ringkasan layar ke memori temporal."""
        memory.record_interaction("VISION_SCREEN_ANALYSIS", analysis.get("app_detected"), analysis.get("context"), {"sensitive": analysis.get("is_sensitive", False)})

    @staticmethod
    def extract_ui_elements(image_path: str):
        """Phase 3: UI-ED (User Interface Element Detection) menggunakan OpenCV."""
        try:
            img = cv2.imread(image_path)
            if img is None: return []
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            edges = cv2.Canny(blur, 50, 150)
            
            # Deteksi kontur
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            elements = []
            
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w < 40 or h < 20: continue # Terlalu kecil
                if w > img.shape[1] * 0.95: continue # Terlalu lebar (mungkin frame)
                
                aspect_ratio = w / float(h)
                category = "generic_component"
                
                # Heuristik Kategorisasi
                if 0.7 < aspect_ratio < 1.3:
                    category = "action_icon_or_button"
                elif aspect_ratio > 3.5:
                    category = "input_field_or_text_area"
                elif h > 100:
                    category = "container_or_card"
                
                elements.append({
                    "type": category,
                    "bounds": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "center": {"x": int(x + w//2), "y": int(y + h//2)},
                    "score": round(1.0 - (1.0/aspect_ratio if aspect_ratio > 1 else aspect_ratio), 2)
                })
                
            # Mengambil 15 elemen yang paling menonjol
            elements = sorted(elements, key=lambda e: e["bounds"]["width"] * e["bounds"]["height"], reverse=True)
            return elements[:15]
        except Exception as e:
            log.error(f"UI Extraction Failed: {e}")
            return []

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = ScreenVisionIntelligence.analyze_screen(sys.argv[1])
        print(json.dumps(res, indent=2))
