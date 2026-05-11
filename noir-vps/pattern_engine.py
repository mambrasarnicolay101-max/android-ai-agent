import os
import json
import time
from collections import Counter
from datetime import datetime

class PatternRecognitionEngine:
    """
    PILAR 3: PROACTIVE PATTERN RECOGNITION (v1.0)
    Menganalisis histori perintah untuk mendeteksi rutinitas 
    dan mengusulkan otomatisasi proaktif.
    """
    
    HISTORY_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "command_history.json")
    
    def __init__(self):
        self.history = []
        self.load_history()
        
    def load_history(self):
        if os.path.exists(self.HISTORY_FILE):
            try:
                with open(self.HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = []

    def record_command(self, action_type, params=None):
        """Mencatat setiap perintah yang dieksekusi ke dalam histori pola."""
        entry = {
            "timestamp": time.time(),
            "action": action_type,
            "params": params
        }
        self.history.append(entry)
        # Simpan 1000 perintah terakhir
        if len(self.history) > 1000:
            self.history.pop(0)
        
        os.makedirs(os.path.dirname(self.HISTORY_FILE), exist_ok=True)
        with open(self.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

    def analyze_routines(self):
        """Mendeteksi urutan perintah yang sering berulang (Bigrams/Trigrams)."""
        if len(self.history) < 5:
            return None
            
        actions = [h["action"] for h in self.history]
        
        # Cari Bigrams (pasangan perintah berurutan)
        bigrams = [(actions[i], actions[i+1]) for i in range(len(actions)-1)]
        common_bigrams = Counter(bigrams).most_common(3)
        
        proposals = []
        for (a, b), count in common_bigrams:
            if count >= 3: # Terjadi minimal 3 kali
                proposals.append({
                    "pattern": f"{a} -> {b}",
                    "count": count,
                    "suggestion": f"Otomatisasi: Jalankan {b} segera setelah {a} selesai."
                })
        
        return proposals

    def get_proactive_suggestion(self):
        """Memberikan saran cerdas berdasarkan pola terakhir."""
        routines = self.analyze_routines()
        if not routines:
            return "Noir sedang mengamati pola penggunaan Anda untuk membangun rutinitas otonom."
            
        top = routines[0]
        return f"Terdeteksi Pola: Anda sering menjalankan '{top['pattern']}'. Ingin saya mengotomatiskan ini?"

pattern_engine = PatternRecognitionEngine()

if __name__ == "__main__":
    # Test
    pe = PatternRecognitionEngine()
    pe.record_command("gps")
    pe.record_command("screenshot")
    pe.record_command("gps")
    pe.record_command("screenshot")
    pe.record_command("gps")
    pe.record_command("screenshot")
    
    print(pe.get_proactive_suggestion())
