import os, sys, json, logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("FinalAudit")

def run_deep_audit():
    log.info("=== STARTING FINAL DEEP AUDIT [SINGULARITY MODE] ===")
    
    # 1. Environment Check
    env_path = ".env"
    if os.path.exists(env_path):
        log.info("[OK] .env file found.")
        with open(env_path, "r") as f:
            content = f.read()
            critical_keys = ["NOIR_VPS_IP", "GEMINI_API_KEY", "GROQ_API_KEY"]
            for key in critical_keys:
                if key in content:
                    log.info(f" [OK] Key {key} is present.")
                else:
                    log.warning(f" [!] Key {key} is missing in .env")
    else:
        log.error("[ERROR] .env file MISSING!")

    # 2. Directory Structure Check
    required_dirs = ["noir-vps", "noir-ui", "noir-core", "knowledge", "docs/system_evolution"]
    for d in required_dirs:
        if os.path.exists(d):
            log.info(f"[OK] Directory '{d}' exists.")
        else:
            log.error(f"[ERROR] Directory '{d}' is MISSING!")

    # 3. Pillar Import Audit
    log.info("--- Auditing Pillar Reachability ---")
    sys.path.append(os.path.abspath("noir-vps"))
    pillars = [
        "sovereign_orchestrator", "ai_router", "vector_memory", "evolution_engine",
        "red_blue_arena", "battle_logger", "grand_singularity_cycle", "autonomous_pentester"
    ]
    for p in pillars:
        try:
            __import__(p)
            log.info(f" [OK] Pillar '{p}' is importable.")
        except Exception as e:
            log.error(f" [ERROR] Pillar '{p}' FAILED to import: {e}")

    # 4. Web Server Integrity
    index_path = "noir-ui/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()
            if "BATTLE INTELLIGENCE" in html and "GRAND SINGULARITY" in html:
                log.info("[OK] Dashboard UI is up-to-date with new features.")
            else:
                log.warning("[!] Dashboard UI might be missing new sections.")
    
    log.info("=== DEEP AUDIT COMPLETED ===")

if __name__ == "__main__":
    run_deep_audit()
