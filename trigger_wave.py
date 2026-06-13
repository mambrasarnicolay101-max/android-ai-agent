import requests
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

url = "http://8.215.23.17/api/chat"
headers = {
    "Authorization": "Bearer NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026",
    "Content-Type": "application/json"
}
data = {"message": "/simulate_wave HIGH"}

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
except Exception as e:
    print("ERROR:", e)
