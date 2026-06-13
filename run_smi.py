import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
vps_dir = os.path.join(base_dir, "noir-vps")
if vps_dir not in sys.path:
    sys.path.insert(0, vps_dir)

from sovereign_maturity_index import SovereignMaturityIndex
import json

if __name__ == "__main__":
    try:
        smi = SovereignMaturityIndex()
        res = smi.calculate_index()
        print("SMI CALCULATION RESULT:")
        print(json.dumps(res, indent=4))
    except Exception as e:
        print(f"ERROR: {e}")
