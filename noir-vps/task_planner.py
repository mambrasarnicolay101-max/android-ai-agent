import os
import json
import time
import uuid

PLAN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge", "task_plans.json"))

class TaskPlanner:
    @staticmethod
    def _load_plans():
        if not os.path.exists(PLAN_FILE):
            os.makedirs(os.path.dirname(PLAN_FILE), exist_ok=True)
            with open(PLAN_FILE, "w") as f:
                json.dump({}, f)
            return {}
        try:
            with open(PLAN_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _save_plans(plans):
        os.makedirs(os.path.dirname(PLAN_FILE), exist_ok=True)
        with open(PLAN_FILE, "w") as f:
            json.dump(plans, f, indent=4)

    @classmethod
    def create_plan(cls, title, steps):
        plans = cls._load_plans()
        plan_id = str(uuid.uuid4())[:8]
        
        formatted_steps = []
        for i, step in enumerate(steps):
            if isinstance(step, str):
                formatted_steps.append({
                    "id": i,
                    "title": step,
                    "status": "pending"
                })
            else:
                formatted_steps.append({
                    "id": step.get("id", i),
                    "title": step.get("title", ""),
                    "status": step.get("status", "pending")
                })

        plans[plan_id] = {
            "id": plan_id,
            "title": title,
            "created_at": time.time(),
            "updated_at": time.time(),
            "status": "pending",
            "steps": formatted_steps
        }
        cls._save_plans(plans)
        return plans[plan_id]

    @classmethod
    def update_step(cls, plan_id, step_id, status):
        plans = cls._load_plans()
        if plan_id not in plans:
            return None
        
        plan = plans[plan_id]
        step_found = False
        for step in plan["steps"]:
            if str(step["id"]) == str(step_id):
                step["status"] = status
                step_found = True
                break
        
        if not step_found:
            return None
            
        plan["updated_at"] = time.time()
        
        statuses = [s["status"] for s in plan["steps"]]
        if all(s == "done" for s in statuses):
            plan["status"] = "done"
        elif any(s == "failed" for s in statuses):
            plan["status"] = "failed"
        elif any(s == "in_progress" for s in statuses) or any(s == "done" for s in statuses):
            plan["status"] = "in_progress"
        else:
            plan["status"] = "pending"
            
        cls._save_plans(plans)
        return plan

    @classmethod
    def get_all_plans(cls):
        plans = cls._load_plans()
        return sorted(plans.values(), key=lambda x: x["created_at"], reverse=True)
