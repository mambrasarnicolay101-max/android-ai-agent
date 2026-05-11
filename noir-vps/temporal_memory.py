#!/usr/bin/env python3
"""
NOIR SOVEREIGN v17.5 — TEMPORAL MEMORY SYSTEM
=============================================
Sistem memori jangka panjang untuk menyimpan konteks, 
preferensi user, dan keberhasilan tugas masa lalu.
"""

import os, json, time, logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger("SovereignMemory")

class TemporalMemory:
    def __init__(self, memory_file=None):
        if memory_file is None:
            self.memory_file = str(Path(__file__).resolve().parent.parent / "knowledge" / "temporal_memory.json")
        else:
            self.memory_file = memory_file
        # Ensure knowledge dir exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        self.memory = self._load_memory()

    def _load_memory(self):
        data = {"interactions": [], "preferences": {}, "learned_skills": []}
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        # Merge with default keys to handle legacy structures
                        data.update(loaded)
                        if "interactions" not in data:
                            data["interactions"] = data.get("memory", []) # migrate old memory
            except:
                pass
        
        # Guarantee minimum structure
        for key in ["interactions", "preferences", "learned_skills"]:
            if key not in data:
                data[key] = [] if key != "preferences" else {}
                
        return data

    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=4)

    def record_interaction(self, user_id, input_text, response_text, metadata=None):
        """Mencatat interaksi untuk pembelajaran masa depan."""
        entry = {
            "timestamp": time.time(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "input": input_text,
            "output": response_text,
            "metadata": metadata or {}
        }
        self.memory["interactions"].append(entry)
        
        # Batasi memori interaksi agar tidak membengkak (max 500)
        if len(self.memory["interactions"]) > 500:
            self.memory["interactions"] = self.memory["interactions"][-500:]
            
        self._save_memory()
        log.info(f"🧠 Memory Recorded: {input_text[:30]}...")

    def update_preference(self, key, value):
        """Menyimpan preferensi user yang dipelajari secara otonom."""
        self.memory["preferences"][key] = value
        self._save_memory()
        log.info(f"🎯 Preference Learned: {key} = {value}")

    def get_context_for_topic(self, topic):
        """Mencari memori relevan berdasarkan kata kunci."""
        relevant = [i for i in self.memory["interactions"] if topic.lower() in i["input"].lower()]
        return relevant[-5:] # Ambil 5 terakhir

    def get_stats(self):
        return {
            "total_interactions": len(self.memory["interactions"]),
            "known_preferences": len(self.memory["preferences"]),
            "last_interaction": self.memory["interactions"][-1]["date"] if self.memory["interactions"] else "N/A"
        }

# --- SINGLETON INSTANCE ---
# Use this global instance to prevent Race Conditions across multiple modules
global_memory = TemporalMemory()

if __name__ == "__main__":
    # Test
    mem = TemporalMemory("knowledge/test_memory.json")
    mem.record_interaction("USER_ASUS", "Deploy fixed brain", "Deployment successful")
    print(mem.get_stats())
