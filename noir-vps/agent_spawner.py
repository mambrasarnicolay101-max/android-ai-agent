import os
import json
import time
import uuid
import threading
from ai_router import OmniRouter

AGENT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge", "agents.json"))

_running_agents = {}

class AgentSpawner:
    @staticmethod
    def _load_agents():
        if not os.path.exists(AGENT_FILE):
            os.makedirs(os.path.dirname(AGENT_FILE), exist_ok=True)
            with open(AGENT_FILE, "w") as f:
                json.dump({}, f)
            return {}
        try:
            with open(AGENT_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _save_agents(agents):
        os.makedirs(os.path.dirname(AGENT_FILE), exist_ok=True)
        with open(AGENT_FILE, "w") as f:
            json.dump(agents, f, indent=4)

    @classmethod
    def spawn(cls, task_name, prompt, provider="gemini"):
        agents = cls._load_agents()
        agent_id = str(uuid.uuid4())[:8]
        
        agent_info = {
            "id": agent_id,
            "task_name": task_name,
            "prompt": prompt,
            "provider": provider,
            "status": "running",
            "created_at": time.time(),
            "finished_at": None,
            "output": "",
            "logs": [f"[{time.strftime('%H:%M:%S')}] Subagent spawned on provider: {provider}."]
        }
        
        agents[agent_id] = agent_info
        cls._save_agents(agents)
        
        thread = threading.Thread(target=cls._run_agent_thread, args=(agent_id, task_name, prompt, provider), daemon=True)
        _running_agents[agent_id] = thread
        thread.start()
        
        return agent_info

    @classmethod
    def _run_agent_thread(cls, agent_id, task_name, prompt, provider):
        try:
            cls._append_log(agent_id, "Memulai pemrosesan AI request...")
            
            task_type = "general"
            if any(k in prompt.lower() for k in ["code", "program", "fungsi", "coding", "buat", "script"]):
                task_type = "coding"
            
            res = OmniRouter.query(prompt, task_type=task_type)
            
            agents = cls._load_agents()
            if agent_id in agents:
                agent = agents[agent_id]
                if agent["status"] == "running":
                    agent["status"] = "completed"
                    agent["output"] = res
                    agent["finished_at"] = time.time()
                    agent["logs"].append(f"[{time.strftime('%H:%M:%S')}] Sukses menyelesaikan tugas.")
                    cls._save_agents(agents)
        except Exception as e:
            agents = cls._load_agents()
            if agent_id in agents:
                agent = agents[agent_id]
                if agent["status"] == "running":
                    agent["status"] = "failed"
                    agent["output"] = f"Error: {str(e)}"
                    agent["finished_at"] = time.time()
                    agent["logs"].append(f"[{time.strftime('%H:%M:%S')}] Kegagalan eksekusi: {str(e)}")
                    cls._save_agents(agents)

    @classmethod
    def _append_log(cls, agent_id, log_msg):
        agents = cls._load_agents()
        if agent_id in agents:
            agents[agent_id]["logs"].append(f"[{time.strftime('%H:%M:%S')}] {log_msg}")
            cls._save_agents(agents)

    @classmethod
    def get_all_agents(cls):
        agents = cls._load_agents()
        return sorted(agents.values(), key=lambda x: x["created_at"], reverse=True)

    @classmethod
    def kill_agent(cls, agent_id):
        agents = cls._load_agents()
        if agent_id not in agents:
            return None
        
        agent = agents[agent_id]
        if agent["status"] == "running":
            agent["status"] = "killed"
            agent["finished_at"] = time.time()
            agent["logs"].append(f"[{time.strftime('%H:%M:%S')}] Subagent dihentikan secara paksa oleh pengguna.")
            cls._save_agents(agents)
        
        return agent
