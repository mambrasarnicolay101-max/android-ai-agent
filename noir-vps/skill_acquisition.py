import os, json, logging, requests
from ai_router import OmniRouter, ResearchEngine

log = logging.getLogger("SkillAcquisition")

SKILL_LIBRARY_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "skill_library.json")

class SkillAcquisitionEngine:
    """Engine untuk menemukan dan mengintegrasikan alat AI baru secara otonom."""
    
    @staticmethod
    def discover_and_integrate(topic: str):
        log.info(f" Discovering new AI tools for: {topic}")
        
        # 1. Real Web Research
        search_query = f"best free API or tool for {topic} with documentation and endpoint"
        search_results = OmniRouter.web_search(search_query)
        
        # 2. Deep Analysis & Code Generation
        analysis_prompt = f"""
        Analyze these search results: {search_results}
        Find the BEST FREE AI tool/API for '{topic}'.
        Return a JSON object with:
        - name: Tool name
        - endpoint: Base API URL
        - method: GET/POST
        - auth: "None" or "API_Key"
        - description: Why this is useful
        - payload_template: Example JSON if POST
        - test_instruction: How to verify it works
        """
        
        analysis = OmniRouter.query_gemini(analysis_prompt, response_json=True)
        
        try:
            tool_data = json.loads(analysis)
            # 3. Integration & Catalyst Absorption
            SkillAcquisitionEngine.save_skill(tool_data)
            
            # Record in Evolution Engine
            from evolution_engine import evolution_engine
            evolution_engine.propose_evolution(
                title=f"New Skill Integrated: {tool_data['name']}",
                description=f"Noir has autonomously learned to use {tool_data['name']} for {topic}.",
                changes={"skill": tool_data},
                complexity=3
            )
            
            return tool_data
        except Exception as e:
            log.error(f"Autonomous integration failed: {e}")
            return {"error": str(e)}

    @staticmethod
    def save_skill(tool_data: dict):
        library = {}
        if os.path.exists(SKILL_LIBRARY_PATH):
            with open(SKILL_LIBRARY_PATH, "r") as f:
                library = json.load(f)
        
        library[tool_data["name"]] = tool_data
        
        with open(SKILL_LIBRARY_PATH, "w") as f:
            json.dump(library, f, indent=4)
        log.info(f" Skill integrated: {tool_data['name']}")

    @staticmethod
    def get_integrated_skills():
        if os.path.exists(SKILL_LIBRARY_PATH):
            with open(SKILL_LIBRARY_PATH, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def execute_skill(skill_name: str, user_input: str):
        skills = SkillAcquisitionEngine.get_integrated_skills()
        if skill_name not in skills:
            return f"Skill {skill_name} belum terintegrasi."
        
        tool = skills[skill_name]
        log.info(f" Executing dynamic skill: {skill_name}")
        
        # Logic eksekusi dinamis (DISABLED in v16 Stabilization)
        return {"status": "PAUSED", "message": f"Dynamic execution for '{skill_name}' is paused to save tokens."}
