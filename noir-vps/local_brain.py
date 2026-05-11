import re
import random
from datetime import datetime

class LocalNeuralBrain:
    """
    PILAR 1: OFFLINE LOCAL BRAIN (v1.0)
    Mesin inferensi lokal untuk Noir Sovereign.
    Mampu menangani intent dasar dan kendali perangkat tanpa API Cloud.
    """
    
    INTENTS = {
        "screenshot": [r"screenshot", r"tangkap layar", r"capture", r"foto layar"],
        "gps": [r"lokasi", r"gps", r"location", r"posisi", r"dimana"],
        "camera": [r"camera", r"kamera", r"foto", r"potret", r"shoot"],
        "audio": [r"audio", r"rekam", r"suara", r"voice", r"record"],
        "status": [r"status", r"kondisi", r"health", r"sehat", r"aktif"],
        "identity": [r"siapa", r"identitas", r"who are you", r"pencipta"],
        "vibrate": [r"getar", r"vibrate", r"alert", r"ping"],
        "clean": [r"bersih", r"clear", r"hapus log", r"optimize"]
    }
    
    RESPONSES = {
        "screenshot": ["Baik, mengambil screenshot sekarang.", "Layar berhasil ditangkap.", "Memproses permintaan screenshot."],
        "gps": ["Melacak koordinat GPS perangkat...", "Mengambil data lokasi terakhir."],
        "identity": ["Saya adalah Noir Sovereign AI Agent v21.1, entitas otonom Anda.", "Noir Sovereign di sini, siap melayani."],
        "status": ["Sistem Noir Sovereign V21.1 stabil. Memori Lokal: Aktif. Bypass SSL: Aktif."],
        "unknown": ["Perintah diterima, namun saya memerlukan koneksi Cloud untuk analisis mendalam.", "Neural Link lokal terbatas, silakan coba perintah yang lebih spesifik."]
    }

    def process(self, text):
        """Mendeteksi intent dan memberikan respon offline."""
        text = text.lower()
        detected_intent = None
        
        for intent, patterns in self.INTENTS.items():
            if any(re.search(p, text) for p in patterns):
                detected_intent = intent
                break
        
        if detected_intent:
            response = random.choice(self.RESPONSES.get(detected_intent, ["Permintaan sedang diproses."]))
            return {
                "response": response,
                "intent": detected_intent,
                "confidence": 0.95,
                "offline": True,
                "action": {"type": detected_intent} if detected_intent in ["screenshot", "gps", "camera", "audio", "vibrate"] else None
            }
        
        return {
            "response": random.choice(self.RESPONSES["unknown"]),
            "intent": "unknown",
            "confidence": 0.3,
            "offline": True,
            "action": None
        }

local_brain = LocalNeuralBrain()

if __name__ == "__main__":
    # Test
    brain = LocalNeuralBrain()
    print(brain.process("Ambilkan screenshot layar"))
    print(brain.process("Siapa namamu?"))
    print(brain.process("Cek lokasi sekarang"))
