import sys, os, logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "noir-vps"))

try:
    from neural_architect import NeuralArchitect
except ImportError:
    sys.path.append(str(BASE_DIR))
    from neural_architect import NeuralArchitect

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

if __name__ == "__main__":
    print("[SYSTEM] Triggering First Elite Optimization Audit...")
    try:
        NeuralArchitect.self_audit_and_design()
        print("\n[SUCCESS] Optimization Proposal Submitted to Evolution Engine.")
        print("Check your Dashboard under the 'EVOLUTION' panel to approve the changes.")
    except Exception as e:
        print(f"\n[ERROR] Optimization trigger failed: {e}")
