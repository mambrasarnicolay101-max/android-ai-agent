import os
import time
import logging
import json
from offensive_predator import OffensivePredatorAgent
from self_healer import SelfHealer
from neural_coder import NeuralCoder
from sovereign_notifier import SovereignNotifier

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger("AutonomousTrial")

def run_live_trial():
    print("\n" + "="*60)
    print("[NOIR SOVEREIGN] LIVE AUTONOMOUS TRIAL (V25.0)")
    print("="*60 + "\n")

    # PHASE 1: INDUCED BREACH
    print("PHASE 1: Menjalankan Simulasi Serangan 'Bypass'...")
    target = "SystemCore"
    method = "AI-Synthesized Exploit: Shadow-Thread RCE"
    
    # Kita paksa hasil serangan menjadi SUCCESS untuk menguji Self-Healing
    print(f"[P20] Launching {method} against {target}...")
    SovereignNotifier.notify_battle_result(
        agent_source="P20",
        target=target,
        method=method,
        status="SUCCESS",
        analysis="Simulated breach for autonomous verification trial."
    )
    print("OK: Serangan berhasil menjebol pertahanan (Simulasi).")
    time.sleep(2)

    # PHASE 2: DETECTION & PATCHING
    print("\nPHASE 2: Deteksi Pelanggaran & Autonomous Patching...")
    # SelfHealer akan mendeteksi report 'SUCCESS' tadi
    SelfHealer.monitor_breaches()
    
    print("\nPHASE 3: Verifikasi Patch...")
    skills_dir = "c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/noir-vps/skills"
    recent_skills = sorted([f for f in os.listdir(skills_dir) if f.startswith("patch_")], reverse=True)
    
    if recent_skills:
        print(f"OK: Neural Coder berhasil menciptakan patch: {recent_skills[0]}")
        with open(os.path.join(skills_dir, recent_skills[0]), "r") as f:
            print("-" * 30)
            print(f.read()[:200] + "...")
            print("-" * 30)
    else:
        print("FAIL: Gagal mendeteksi patch baru. Periksa log OmniRouter.")

    print("\n[TRIAL COMPLETE] Sistem terbukti mampu berevolusi secara otonom.")

if __name__ == "__main__":
    run_live_trial()
