import os, subprocess, logging, json

log = logging.getLogger("EvolutionBridge")

class EvolutionBridge:
    """Bridges AI Research with Physical Code Evolution (Phase 6)."""
    
    BASE_DIR = "/root/noir-agent"
    
    @staticmethod
    def apply_evolution_patch(component: str, file_path: str, new_code: str):
        """Applies AI-generated improvements to the source code."""
        abs_path = os.path.join(EvolutionBridge.BASE_DIR, component, file_path)
        if not os.path.exists(abs_path):
            log.error(f"Evolution Target Missing: {abs_path}")
            return False
            
        log.info(f" Evolving {component}/{file_path}...")
        try:
            with open(abs_path, "w") as f:
                f.write(new_code)
            return True
        except Exception as e:
            log.error(f"Evolution Patch Failed: {e}")
            return False

    @staticmethod
    def trigger_apk_evolution():
        """Initiates a background APK rebuild via Buildozer on VPS."""
        log.info(" Triggering APK Evolution Build...")
        try:
            # We run this in a detached process to not block the brain
            cmd = "cd /root/noir-agent && docker exec noir-researcher buildozer android debug"
            subprocess.Popen(cmd, shell=True)
            return "APK Build Initiated in background."
        except Exception as e:
            return f"Build Trigger Error: {e}"

    @staticmethod
    def trigger_dashboard_evolution():
        """Reloads the dashboard service after code changes."""
        log.info(" Triggering Dashboard Visual Evolution...")
        try:
            cmd = "cd /root/noir-agent && docker compose restart noir-dashboard"
            subprocess.run(cmd, shell=True)
            return "Dashboard evolved and reloaded."
        except Exception as e:
            return f"Dashboard Reload Error: {e}"

# Integration into Brain loop
def check_for_evolution_proposals():
    # Placeholder: Brain will query the Researcher for improvements
    pass
