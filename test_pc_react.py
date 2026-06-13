import requests
import json

# Konfigurasi VPS dan Otentikasi
VPS_IP = "8.215.23.17"
AUTH_TOKEN = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026"
URL = f"http://{VPS_IP}/api/chat"

# Prompt yang memicu PC Agent mode
payload = {
    "message": "di pc, tolong buatkan file test_agent.txt dengan isi 'Berhasil menghubungkan Otak dan Otot!' dan jalankan perintah systeminfo"
}

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

print(f"Mengirim instruksi ke VPS Noir Sovereign ({VPS_IP})...")
print(f"Pesan: {payload['message']}\n")

try:
    r = requests.post(URL, json=payload, headers=headers)
    print("--- HASIL DARI AI ---")
    if r.status_code == 200:
        data = r.json()
        print(data.get("reply", "Tidak ada balasan teks."))
    else:
        print(f"Error {r.status_code}: {r.text}")
except Exception as e:
    print(f"Gagal menghubungi VPS: {e}")
