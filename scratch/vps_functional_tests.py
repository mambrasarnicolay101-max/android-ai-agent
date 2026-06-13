# -*- coding: utf-8 -*-
"""
NOIR SOVEREIGN V30.1 — UJI FUNGSI SISTEM (DIAGNOSTIK ENDPOINT LIVE)
Menguji seluruh fungsi REST API di VPS secara mendalam.
"""
import requests
import json
import os
import sys
from dotenv import load_dotenv

# Paksa UTF-8 output pada terminal Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

load_dotenv()

VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
BASE_URL = f"http://{VPS_IP}"
API_KEY = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def print_banner():
    print("=" * 65)
    print("  🌌 NOIR SOVEREIGN V30.1 — UJI FUNGSI SISTEM MENYELURUH 🌌")
    print("=" * 65)
    print(f"  Target Gateway : {BASE_URL}")
    print(f"  Otentikasi     : Bearer {API_KEY[:10]}...")
    print("=" * 65)

def test_endpoint(name, method, path, payload=None, expect_auth_failure=False):
    url = f"{BASE_URL}{path}"
    headers = HEADERS if not expect_auth_failure else {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload, timeout=10)
        else:
            return False, "Method not supported"
        
        status = response.status_code
        try:
            body = response.json()
        except:
            body = response.text[:150]

        # Validasi
        if expect_auth_failure:
            if status in (401, 403):
                return True, f"HTTP {status} (Ditolak sesuai ekspektasi Zero-Trust)"
            else:
                return False, f"HTTP {status} (Seharusnya ditolak tapi malah lolos!)"
        
        if status == 200:
            if isinstance(body, dict):
                # Memeriksa key sukses standar di beberapa endpoint
                success_val = body.get("success", body.get("ok", True))
                if success_val is False:
                    return False, f"HTTP 200 dengan kegagalan internal: {body.get('reason', body.get('error', 'Unknown error'))}"
                
            return True, f"HTTP 200 OK | Response: {str(body)[:80]}..."
        else:
            return False, f"HTTP {status} | Error: {str(body)[:100]}"
            
    except Exception as e:
        return False, f"Koneksi Gagal: {e}"

def run_suite():
    print_banner()
    
    test_cases = [
        # (Nama Pengujian, HTTP Method, Path, Payload, Expect Auth Failure)
        (
            "1. Liveness & Health Check (Publik)", 
            "GET", 
            "/health", 
            None, 
            False
        ),
        (
            "2. Zero-Trust Security Check (Coba tanpa token)", 
            "POST", 
            "/api/logs", 
            {"device_id": "TEST_DEVICE", "message": "Zero-trust test log"}, 
            True
        ),
        (
            "3. Dashboard Smart Status (Private)", 
            "GET", 
            "/api/status", 
            None, 
            False
        ),
        (
            "4. Central Logger System (Private)", 
            "POST", 
            "/api/logs", 
            {
                "device_id": "TEST_DIAGNOSTIC", 
                "level": "INFO", 
                "message": "Noir Sovereign V30.1 Automated Functional Diagnostic Probe."
            }, 
            False
        ),
        (
            "5. Active AI Provider Query (Publik)", 
            "GET", 
            "/api/brain/provider", 
            None, 
            False
        ),
        (
            "6. Chat History Retrieval (Publik)", 
            "GET", 
            "/api/chat/history", 
            None, 
            False
        ),
        (
            "7. Neural Command & AI Chat Relay (Private)", 
            "POST", 
            "/api/chat", 
            {"message": "Halo AI, periksa status modul neural Anda.", "device_id": "REDMI_NOTE_14"}, 
            False
        ),
        (
            "8. Sovereign Evolution Proposals (Private)", 
            "GET", 
            "/api/evolutions", 
            None, 
            False
        ),
        (
            "9. Advanced HID BadUSB Scenarios (Private)", 
            "GET", 
            "/api/badusb/scenarios", 
            None, 
            False
        ),
        (
            "10. Cyber Warfare Battle Logger Stats (Private)", 
            "GET", 
            "/api/battle/stats", 
            None, 
            False
        ),
        (
            "11. Sovereign Maturity Index (SMI) Summary (Private)", 
            "GET", 
            "/api/summary", 
            None, 
            False
        )
    ]
    
    passed_count = 0
    total_count = len(test_cases)
    
    for name, method, path, payload, expect_fail in test_cases:
        print(f"🔄 {name}...")
        success, msg = test_endpoint(name, method, path, payload, expect_fail)
        if success:
            print(f"   🟢 SUCCESS | {msg}")
            passed_count += 1
        else:
            print(f"   🔴 FAILED  | {msg}")
        print("-" * 65)
        
    print("\n" + "=" * 65)
    print("                      RINGKASAN UJI FUNGSI")
    print("=" * 65)
    print(f"  Total Pengujian : {total_count}")
    print(f"  Lolos           : {passed_count} / {total_count}")
    
    if passed_count == total_count:
        print("  Status Akhir    : 🟢 KESELURUHAN FUNGSI BERJALAN SEMPURNA (100% OK)")
    else:
        print(f"  Status Akhir    : 🔴 DEGRADASI SISTEM ({total_count - passed_count} FUNGSI GAGAL)")
    print("=" * 65)

if __name__ == "__main__":
    run_suite()
