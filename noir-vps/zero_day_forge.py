import os
import json
import logging
from ai_router import OmniRouter
import glob

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [FORGE] %(message)s")
log = logging.getLogger("ZeroDayForge")

ARSENAL_DIR = os.path.join(os.path.dirname(__file__), "arsenal")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")

def forge_weapon_from_cve(cve_id, description):
    log.info(f"Membangkitkan Forge untuk {cve_id}...")
    prompt = f"""Kamu adalah Noir Sovereign, AI Offensif tingkat Apex.
Tugas: Buat sebuah skrip Eksploitasi (Python) yang sangat efektif sebagai senjata serangan konsep (*Proof of Concept*) untuk kerentanan berikut.
CVE ID: {cve_id}
Deskripsi: {description}

Syarat:
1. Skrip harus menggunakan modul 'requests' atau 'socket' standar.
2. Harus ada fungsi 'def run_exploit(target_url):'
3. Hanya keluarkan KODE PYTHON mentah tanpa komentar Markdown (```python) di awal atau akhir, murni skrip.
4. Gunakan arsitektur Polymorphic (Junk Variables) yang sudah Anda pelajari untuk mengelabui deteksi.
"""
    # Memaksa menggunakan provider lokal gratis (Llama-3 via Groq/Ollama) untuk penghematan
    raw_script = OmniRouter.query(prompt, task_type="coding")
    
    if raw_script:
        # Bersihkan markdown artifact jika masih ada
        if raw_script.startswith("```"):
            lines = raw_script.split("\n")
            if len(lines) > 2:
                raw_script = "\n".join(lines[1:-1])
        
        file_path = os.path.join(ARSENAL_DIR, f"exploit_{cve_id.replace('-', '_').lower()}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# WEAPON FORGE - SYNTHESIZED BY NOIR SOVEREIGN\n")
            f.write(f"# TARGET: {cve_id}\n\n")
            f.write(raw_script)
            
        log.info(f"Senjata berhasil disintesis dan disimpan: {file_path}")
        return True
    return False

def scan_memories_and_forge():
    log.info("Memindai memori intelijen (CVE) yang belum di-forge...")
    os.makedirs(ARSENAL_DIR, exist_ok=True)
    
    # Cari file memori osint_cve_*.json
    cve_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "osint_cve_*.json"))
    for file in cve_files:
        with open(file, "r") as f:
            try:
                data = json.load(f)
                threats = data.get("latest_threats", [])
                for threat in threats:
                    cve_id = threat.get("id")
                    desc = threat.get("description")
                    weapon_file = os.path.join(ARSENAL_DIR, f"exploit_{cve_id.replace('-', '_').lower()}.py")
                    
                    if not os.path.exists(weapon_file):
                        forge_weapon_from_cve(cve_id, desc)
                    else:
                        log.info(f"Senjata untuk {cve_id} sudah ada di Arsenal.")
            except Exception as e:
                log.error(f"Gagal membaca memori {file}: {e}")

if __name__ == "__main__":
    scan_memories_and_forge()
