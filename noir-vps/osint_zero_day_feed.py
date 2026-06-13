import requests
import json
import logging
from datetime import datetime

# Attempt to import cloud memory
try:
    from cloud_memory_client import CloudMemoryClient
except ImportError:
    CloudMemoryClient = None
from ai_router import OmniRouter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [0-DAY-FEED] %(message)s")
log = logging.getLogger("ZeroDayFeed")

def fetch_latest_cves():
    log.info("Menarik data CVE terbaru dari NVD API (National Vulnerability Database)...")
    # Mengambil 5 CVE terbaru dengan skor kritis
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0/?resultsPerPage=5"
    
    try:
        # Perlu User-Agent khusus agar tidak diblokir NIST
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            vulnerabilities = []
            
            if "vulnerabilities" in data:
                for item in data["vulnerabilities"]:
                    cve = item.get("cve", {})
                    cve_id = cve.get("id", "UNKNOWN_CVE")
                    descriptions = cve.get("descriptions", [])
                    desc_text = descriptions[0].get("value", "") if descriptions else "No description"
                    
                    vuln_info = {
                        "id": cve_id,
                        "description": desc_text,
                        "date_fetched": datetime.now().isoformat()
                    }
                    vulnerabilities.append(vuln_info)
                    
            return vulnerabilities
        else:
            log.error(f"Gagal mengambil CVE. HTTP Status: {response.status_code}")
            return []
    except Exception as e:
        log.error(f"NVD API Error: {e}")
        return []

def store_zero_day_intelligence(vuln_data):
    if not vuln_data:
        log.warning("Tidak ada data kerentanan yang ditarik.")
        return
        
    payload = json.dumps({"latest_threats": vuln_data})
    mem_key = f"osint_cve_{int(datetime.now().timestamp())}"
    
    success = False
    if CloudMemoryClient:
        client = CloudMemoryClient()
        success = client.push_knowledge(mem_key, payload)
        
    if not success:
        log.info("Menyimpan asupan 0-day ke Local Memory...")
        OmniRouter.store_memory(mem_key, {"latest_threats": vuln_data})
    else:
        log.info(f"Asupan intelijen 0-day berhasil diunggah ke VPS dengan kunci: {mem_key}")

if __name__ == "__main__":
    log.info("Mengaktifkan modul OSINT Zero-Day Feed...")
    cves = fetch_latest_cves()
    if cves:
        for c in cves:
            log.info(f"Ditemukan Ancaman: {c['id']}")
        store_zero_day_intelligence(cves)
    log.info("Siklus intelijen selesai.")
