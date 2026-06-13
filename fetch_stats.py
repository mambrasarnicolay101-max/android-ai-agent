import requests
import json

url_battle = "http://8.215.23.17/api/battle/stats"
url_status = "http://8.215.23.17/api/status"

headers = {
    "Authorization": "Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026",
    "Content-Type": "application/json"
}

try:
    print("--- BATTLE STATS ---")
    res_battle = requests.get(url_battle, headers=headers, timeout=10)
    print(json.dumps(res_battle.json(), indent=2))
    
    print("\n--- SYSTEM STATUS ---")
    res_status = requests.get(url_status, headers=headers, timeout=10)
    print(json.dumps(res_status.json(), indent=2))
except Exception as e:
    print("ERROR:", e)
