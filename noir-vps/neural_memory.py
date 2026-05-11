import os
import json
import numpy as np
from datetime import datetime

class NeuralMemory:
    """
    SOVEREIGN NEURAL MEMORY (v1.0)
    Sistem RAG (Retrieval-Augmented Generation) Lokal untuk Noir.
    Menyimpan pengetahuan dan pengalaman tanpa ketergantungan Cloud.
    """
    
    MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "neural_memory.json")
    
    def __init__(self):
        self.memories = []
        self.load_memory()
        
    def load_memory(self):
        if os.path.exists(self.MEMORY_FILE):
            try:
                with open(self.MEMORY_FILE, "r", encoding="utf-8") as f:
                    self.memories = json.load(f)
            except:
                self.memories = []
                
    def save_memory(self):
        os.makedirs(os.path.dirname(self.MEMORY_FILE), exist_ok=True)
        with open(self.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, indent=4)

    def _simple_vectorize(self, text):
        """Vectorization sederhana berbasis frekuensi kata (Bag of Words)."""
        words = text.lower().split()
        unique_words = list(set(words))
        vector = {word: words.count(word) for word in unique_words}
        return vector

    def add_experience(self, content, category="general", source="autonomous"):
        """Menambahkan pengalaman baru ke dalam memori."""
        memory_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "category": category,
            "source": source,
            "vector": self._simple_vectorize(content)
        }
        self.memories.append(memory_entry)
        # Limit memory to 500 entries to keep it fast
        if len(self.memories) > 500:
            self.memories.pop(0)
        self.save_memory()

    def query(self, query_text, top_k=3):
        """Mencari memori yang relevan menggunakan Cosine Similarity sederhana."""
        if not self.memories:
            return []
        
        query_vec = self._simple_vectorize(query_text)
        scores = []
        
        for mem in self.memories:
            mem_vec = mem["vector"]
            # Dot Product
            dot_product = 0
            for word, count in query_vec.items():
                if word in mem_vec:
                    dot_product += count * mem_vec[word]
            
            # Magnitudes
            mag_q = np.sqrt(sum(v**2 for v in query_vec.values()))
            mag_m = np.sqrt(sum(v**2 for v in mem_vec.values()))
            
            if mag_q == 0 or mag_m == 0:
                score = 0
            else:
                score = dot_product / (mag_q * mag_m)
            
            scores.append((score, mem))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1]["content"] for item in scores[:top_k] if item[0] > 0.1]

neural_memory = NeuralMemory()

if __name__ == "__main__":
    # Test
    nm = NeuralMemory()
    nm.add_experience("Cara melakukan bypass SSL di Python adalah menggunakan verify=False", "technical")
    nm.add_experience("Noir Sovereign adalah AI Agent otonom", "identity")
    
    print("Query 'AI Agent':", nm.query("AI Agent"))
    print("Query 'Bypass':", nm.query("Bypass SSL"))
