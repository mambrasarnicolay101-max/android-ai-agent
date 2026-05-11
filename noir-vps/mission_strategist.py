import os
import json
import logging
from datetime import datetime
from ai_router import AIRouter
from swarm_protocol import SwarmBlackboard

log = logging.getLogger("MissionStrategist")

class MissionStrategist:
    """
    PILAR 10: MISSION STRATEGIST
    Tugas: Memecah tugas kompleks menjadi sub-tugas yang dapat dieksekusi oleh pilar lain.
    """
    
    @staticmethod
    def plan_mission(complex_command: str):
        log.info(f"🎯 Planning mission for: {complex_command}")
        
        prompt = f"""
        Anda adalah Noir Mission Strategist (Pilar 10). 
        Tugas Anda adalah memecah perintah kompleks berikut menjadi langkah-langkah teknis yang dapat dieksekusi oleh tim AI Sovereign (Neural Coder, Security Sentinel, dll).
        
        PERINTAH: {complex_command}
        
        Format Output: JSON list of steps.
        """
        
        strategy = AIRouter.query_gemini(prompt)
        # Kirim ke Swarm Bus
        SwarmBlackboard.post_message(
            sender="MissionStrategist",
            target="ALL",
            content={"type": "new_mission", "strategy": strategy, "original_command": complex_command}
        )
        
        return strategy

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    MissionStrategist.plan_mission("Bangun sistem monitoring e-commerce otonom.")
