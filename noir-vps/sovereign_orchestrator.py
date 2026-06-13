"""
SOVEREIGN ORCHESTRATOR v30.0 ─ NOIR SOVEREIGN (MICROSERVICES EDITION)
======================================================================
Pilar Master: Pengendali 25 Pilar Maestro Noir Sovereign
Mengatur siklus belajar, keamanan, dan evolusi secara penuh otonom.

Perubahan v30.0: Menggunakan arsitektur Plugin Registry (Importlib) 
untuk mencegah bloat memory. Pilar hanya dimuat ke RAM saat dieksekusi.
"""
import os, sys, time, logging, threading, importlib

log = logging.getLogger("SovereignOrchestrator")

# ---------- Scheduler & Plugin Registry ----------
_schedule: dict = {}
_running_threads: dict = {}
_threads_lock = threading.Lock()

PLUGIN_MANIFEST = {
    "neural_coder": {"module": "neural_coder", "class": "NeuralCoder", "method": "mass_learn_cycle", "interval": 120},
    "network_sentinel": {"module": "network_sentinel", "class": "NetworkSentinel", "method": "audit_network", "interval": 120},
    "knowledge_absorber": {"module": "knowledge_absorber", "class": "OmniKnowledgeAbsorber", "method": "absorb_external_intelligence", "args": ["Pola Keamanan Lanjutan Python AsyncIO"], "interval": 300},
    "security_sentinel": {"module": "security_sentinel", "class": "SecuritySentinel", "method": "run_full_audit", "interval": 600},
    "autonomous_pentester": {"module": "autonomous_pentester", "class": "AutonomousPentester", "method": "run_self_pentest", "interval": 600},
    "red_blue_arena": {"module": "red_blue_arena", "class": "RedBlueArena", "method": "run_simulation", "instantiate": True, "interval": 600},
    "memory_consolidator": {"module": "memory_consolidator", "class": "MemoryConsolidator", "method": "run_full_consolidation", "interval": 1200},
    "neural_architect": {"module": "neural_architect", "class": "NeuralArchitect", "method": "analyze_system", "interval": 28800},
    "auto_healer": {"module": "self_healer", "class": "SelfHealer", "method": "monitor_and_heal", "interval": 43200},
    "antigravity_core": {"module": "antigravity_intelligence_core", "class": "AntigravityPillar", "method": "run_knowledge_sync", "interval": 21600},
    "mission_strategist": {"module": "mission_strategist", "class": "MissionStrategist", "method": "plan_mission", "args": ["Review and optimize all existing autonomous skills."], "interval": 10800},
    "qa_validator": {"module": "qa_validator", "class": "QAValidator", "method": "validate_code", "args": ["brain.py"], "interval": 14400},
    "ux_weaver": {"module": "ux_weaver", "class": "UXWeaver", "method": "design_ui_component", "args": ["Unified Sovereign Dashboard glassmorphism update."], "interval": 28800},
    "deep_state_memory": {"module": "vector_memory", "class": "VectorMemory", "method": "index_evolution_history", "interval": 21600},
    "dynamic_skills": {"module": "skill_loader", "class": "SovereignSkillLoader", "method": "execute_all", "interval": 300},
    "self_evaluation": {"module": "sovereign_maturity_index", "class": "SovereignMaturityIndex", "method": "calculate_index", "instantiate": True, "interval": 3600},
    "ghost_mirror": {"module": "shadow_node", "class": "ShadowNode", "method": "run_heartbeat_cycle", "interval": 7200},
    "forensic_audit": {"module": "forensic_investigator", "class": "ForensicInvestigatorAgent", "method": "audit_system_integrity", "interval": 14400},
    "hardware_optim": {"module": "hardware_optimizer", "class": "HardwareOptimizerAgent", "method": "optimize_models", "interval": 28800},
    "linguistic_synth": {"module": "linguistic_synthesis", "class": "LinguisticSynthesisAgent", "method": "synthesize_intent", "args": ["Analyze global security posture and optimize local reflexes."], "interval": 10800},
    "strategist": {"module": "mission_strategist", "class": "MissionStrategist", "method": "forecast_next_objective", "interval": 43200},
    "offensive_predator": {"module": "offensive_predator", "class": "OffensivePredatorAgent", "method": "initiate_massive_attack_simulation", "interval": 14400},
    "honeypot_sentinel": {"module": "honeypot_sentinel", "class": "HoneypotSentinel", "method": "deploy_trap", "interval": 7200},
    "distributed_ledger": {"module": "distributed_ledger", "class": "DistributedLedger", "method": "verify_integrity", "interval": 3600},
    "grand_singularity": {"module": "grand_singularity_cycle", "class": "GrandSingularityCycle", "method": "run_cycle", "instantiate": True, "interval": 300},
    "sovereign_builder": {"module": "sovereign_builder", "class": "SovereignBuilder", "method": "autonomous_build_cycle", "interval": 1200},
    "apex_evolution":     {"module": "apex_evolution",       "class": "ApexEvolutionEngine",        "method": "run_recursive_evolution_cycle", "interval": 600},
    "sovereign_defense":  {"module": "sovereign_defense",     "class": "SovereignDefenseFortress",   "method": "run_full_defense_cycle",        "interval": 600},
    # ── V32.0 NEW MODULES ──────────────────────────────────────────────────────
    "cve_arena":          {"module": "noir_cve_arena",        "class": "NoirCVEArena",               "method": "run_full_cycle",  "instantiate": True, "interval": 21600},  # 6 jam sekali
}


def _should_run(key: str, interval_sec: int) -> bool:
    noir_mode = os.environ.get("NOIR_MODE", "FULL").upper()
    heavy_tasks = ["neural_coder", "memory_consolidator", "knowledge_absorber", "deep_state_memory"]
    
    if noir_mode == "LIGHT" and key in heavy_tasks:
        return False
        
    now = time.time()
    last = _schedule.get(key, 0)
    
    with _threads_lock:
        is_running = key in _running_threads and _running_threads[key].is_alive()
    
    if is_running:
        log.debug(f"[ORK] Task '{key}' masih berjalan, melewati siklus ini.")
        return False

    if now - last >= interval_sec:
        _schedule[key] = now
        return True
    return False

def _run_plugin_task(key: str):
    """Memuat dan mengeksekusi plugin secara dinamis dari manifest."""
    config = PLUGIN_MANIFEST[key]
    try:
        log.info(f"[ORK] [PLUGIN] Memulai siklus '{key}'...")
        mod = importlib.import_module(config["module"])
        
        # Get target object (class or instance)
        target_obj = getattr(mod, config["class"])
        
        # If the target needs to be instantiated first (like RedBlueArena())
        if config.get("instantiate", False):
            target_obj = target_obj()
            
        # Get method
        method = getattr(target_obj, config["method"])
        
        # Execute method with or without args
        args = config.get("args", [])
        if args:
            method(*args)
        else:
            method()
            
        log.info(f"[ORK] [PLUGIN] Siklus '{key}' selesai.")
    except Exception as e:
        log.error(f"[ORK] [PLUGIN] Eksekusi '{key}' gagal: {e}")

def _start_task(key: str):
    """Memulai task dalam thread terkelola."""
    t = threading.Thread(target=_run_plugin_task, args=(key,), daemon=True)
    with _threads_lock:
        _running_threads[key] = t
    t.start()

def _report_status_to_dashboard(cycle: int):
    try:
        import requests
        gateway = os.environ.get("NOIR_GATEWAY_URL", "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")).rstrip("/")
        api_key = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        requests.post(f"{gateway}/api/learning/update", headers=headers, json={
            "status": f"Sovereign Orchestrator V30 - Cycle #{cycle} aktif. 25 Pilar Microservices termuat."
        }, timeout=5)
    except: pass

def run_orchestrator():
    log.info("=" * 60)
    log.info("  SOVEREIGN ORCHESTRATOR v30.0 (MICROSERVICES EDITION)")
    log.info("  PLUGIN REGISTRY: 28 TASKS TERDAFTAR")
    log.info("=" * 60)
    cycle = 0

    while True:
        cycle += 1
        log.info(f"\n{'='*40}\n[ORK] SOVEREIGN CYCLE #{cycle}\n{'='*40}")

        # Dinamis menjadwalkan semua task berdasarkan interval di Manifest
        for key, config in PLUGIN_MANIFEST.items():
            if _should_run(key, config["interval"]):
                _start_task(key)

        _report_status_to_dashboard(cycle)

        # Tidur 5 menit (300s) sebelum siklus berikutnya
        log.info("[ORK] Evaluasi manifest selesai. Siklus berikutnya dalam 5 menit...")
        time.sleep(300)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [ORCHESTRATOR] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    run_orchestrator()
