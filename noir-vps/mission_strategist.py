import os, json, time, logging
from ai_router import OmniRouter

log = logging.getLogger("MissionStrategist")

class MissionStrategist:
    """
    Pilar 10 - Mission Strategist
    Menganalisis data memori dan memberikan forecasting strategis.
    """
    
    @staticmethod
    def forecast_next_objective():
        """U-20: Menganalisis kondisi sistem dan memprediksi target evolusi berikutnya."""
        log.info(" [STRAT] Running strategic forecasting...")
        
        # Ambil ringkasan memori terbaru
        try:
            from vector_memory import vector_memory
            recent = vector_memory.query("system development state", n_results=5)
        except:
            recent = ["Initial setup complete.", "19 pillars active."]
            
        prompt = (
            f"Based on these recent system events: {recent}\n\n"
            "Forecast the next 3 logical objectives for the Noir Sovereign AI ecosystem. "
            "Return a clean JSON object with keys: 'forecast', 'probability', 'impact'."
        )
        
        forecast_json = OmniRouter.query(prompt, task_type="reasoning")
        
        # Save to knowledge
        path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "mission_forecast.json")
        try:
            # Pastikan ini valid JSON sebelum simpan
            data = json.loads(forecast_json)
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            log.info(" [STRAT] Mission Forecast updated.")
            return data
        except:
            log.error(f" [STRAT] Forecast failed to parse: {forecast_json}")
            return {"error": "Synthesis in progress"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    MissionStrategist.forecast_next_objective()
