import os
import requests
import json
import time

GATEWAY = "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")
API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("=== NOIR SOVEREIGN: FASE 3 TEST ===")

# Test 1: Polymorphic Engine & Wardriving Intercept
print("\n[TEST 1] Memulai Simulasi Wardriving Intel Relay...")
wardrive_data = {
    "wifi": ["Target_Corp_WiFi_5G", "Home_Net_2.4G", "Hidden_BSSID_00:1A:2B"],
    "bluetooth": ["Smart_Lock_V2", "Admin_iPhone", "BLE_Tracker_99"]
}

payload = {
    "device_id": "REDMI_RADAR",
    "level": "INFO",
    "message": f"WARDRIVE_INTEL: {json.dumps(wardrive_data)}"
}

try:
    print("Mengirim payload intelijen ke API VPS...")
    res = requests.post(f"{GATEWAY}/api/logs", headers=HEADERS, json=payload, timeout=5)
    print(f"Status Respon: {res.status_code}")
    print(f"Isi Respon: {res.json()}")
    if res.status_code == 200 and res.json().get("success"):
        print("[SUCCESS] API Gateway berhasil menyadap dan memproses payload Wardriving.")
    else:
        print("[FAILED] API Gateway gagal memproses payload.")
except Exception as e:
    print(f"[ERROR] Koneksi ke VPS gagal: {e}")

print("\n=== TEST SELESAI ===")

