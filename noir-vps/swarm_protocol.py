import os
import json
import logging
import time
from threading import Lock

log = logging.getLogger("SwarmProtocol")

class SwarmBlackboard:
    """
    PROTOKOL SWARM: Shared Blackboard System
    Tempat di mana 12 pilar Noir saling berkomunikasi secara real-time.
    """
    
    PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "swarm_bus.json")
    _lock = Lock()

    @classmethod
    def post_message(cls, sender: str, target: str, content: dict):
        with cls._lock:
            bus = cls._read_bus()
            msg_id = f"MSG_{int(time.time()*1000)}"
            bus["messages"].append({
                "id": msg_id,
                "sender": sender,
                "target": target,
                "content": content,
                "ts": time.time(),
                "status": "unread"
            })
            # Keep only last 50 messages
            bus["messages"] = bus["messages"][-50:]
            cls._write_bus(bus)
            log.info(f" [SWARM] {sender} -> {target}: {msg_id}")
            return msg_id

    @classmethod
    def get_messages(cls, target: str):
        with cls._lock:
            bus = cls._read_bus()
            relevant = [m for m in bus["messages"] if (m["target"] == target or m["target"] == "ALL") and m["status"] == "unread"]
            for m in relevant:
                m["status"] = "read"
            cls._write_bus(bus)
            return relevant

    @classmethod
    def _read_bus(cls):
        if not os.path.exists(cls.PATH):
            return {"messages": [], "last_update": time.time()}
        try:
            with open(cls.PATH, "r") as f:
                return json.load(f)
        except:
            return {"messages": [], "last_update": time.time()}

    @classmethod
    def _write_bus(cls, data):
        data["last_update"] = time.time()
        os.makedirs(os.path.dirname(cls.PATH), exist_ok=True)
        with open(cls.PATH, "w") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    SwarmBlackboard.post_message("MissionStrategist", "NeuralCoder", {"task": "Write secure login API"})
    print(SwarmBlackboard.get_messages("NeuralCoder"))
