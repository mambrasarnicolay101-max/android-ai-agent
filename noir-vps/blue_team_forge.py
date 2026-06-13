import os
import json
import logging
import time
from ai_router import OmniRouter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [BLUE-TEAM] %(message)s")
log = logging.getLogger("BlueTeamForge")

DEFENSE_DIR = os.path.join(os.path.dirname(__file__), "defense_patches")
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")
BATTLE_LOG = os.path.join(KNOWLEDGE_DIR, "battle_reports.json")

def load_successful_attacks():
    """Membaca log dan mengelompokkan serangan yang berhasil menembus sistem (status SUCCESS)."""
    if not os.path.exists(BATTLE_LOG):
        log.warning("Battle log tidak ditemukan.")
        return {}

    with open(BATTLE_LOG, "r") as f:
        try:
            data = json.load(f)
        except Exception as e:
            log.error(f"Gagal mem-parsing log: {e}")
            return {}

    threat_clusters = {}
    for entry in data:
        if entry.get("status") == "SUCCESS":
            method = entry.get("method", "Unknown")
            if method not in threat_clusters:
                threat_clusters[method] = 1
            else:
                threat_clusters[method] += 1
                
    return threat_clusters

def forge_defense(method_name, frequency):
    log.info(f"Mensintesis Sistem Pertahanan untuk ancaman: {method_name} (Frekuensi Bobol: {frequency}x)")
    prompt = f"""Kamu adalah Noir Sovereign, divisi BLUE TEAM (Defensif).
Tugasmu: Sistem kita berulang kali dibobol oleh vektor serangan berikut: "{method_name}".
Tuliskan 1 skrip Middleware Python/Flask (filter keamanan) YANG EFEKTIF untuk mendeteksi dan memblokir karakteristik ancaman tersebut. 
Wajib menyertakan sebuah fungsi atau kelas `DefenseMiddleware`.

Syarat:
1. Keluarkan HANYA KODE PYTHON murni, tanpa penjelasan markdown, tanpa markdown tag ```.
2. Kode harus bisa diimplementasikan langsung (plug-and-play).
"""
    # Gunakan model 'coding' untuk penulisan skrip pertahanan
    raw_script = OmniRouter.query(prompt, task_type="coding")
    
    if raw_script:
        # Bersihkan markdown artifact jika LLM bandel
        if raw_script.startswith("```"):
            lines = raw_script.split("\n")
            if len(lines) > 2:
                raw_script = "\n".join(lines[1:-1])
                
        safe_name = method_name.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus").lower()
        file_path = os.path.join(DEFENSE_DIR, f"patch_{safe_name}_{int(time.time())}.py")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# SOVEREIGN SHIELD - AUTONOMOUS DEFENSE PATCH\n")
            f.write(f"# MENGATASI ANCAMAN: {method_name}\n")
            f.write(f"# FREKUENSI TEMBUS: {frequency} kali\n\n")
            f.write(raw_script)
            
        log.info(f"Patch pertahanan berhasil di-deploy: {file_path}")
        return True
    return False

def run_cognitive_defense_cycle():
    log.info("Memulai Audit Keamanan Pasca-Pertempuran...")
    threats = load_successful_attacks()
    
    if not threats:
        log.info("Tidak ada ancaman serius yang menembus sistem berdasarkan log.")
        return
        
    log.info(f"Ditemukan {len(threats)} varian serangan sukses yang harus di-patch.")
    
    # Ambil 3 ancaman teratas saja untuk menghindari rate-limit
    sorted_threats = sorted(threats.items(), key=lambda item: item[1], reverse=True)[:3]
    
    for method, freq in sorted_threats:
        # Pengecekan apakah kita sudah mem-patch ancaman ini sebelumnya dapat dikembangkan di iterasi masa depan
        forge_defense(method, freq)
        time.sleep(3) # Jeda agar tidak terkena limit API/Ollama

if __name__ == "__main__":
    os.makedirs(DEFENSE_DIR, exist_ok=True)
    run_cognitive_defense_cycle()
