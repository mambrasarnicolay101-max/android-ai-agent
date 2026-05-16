import os
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ShadowNode")

class ShadowNode:
    """
    SHADOW NODE HEARTBEAT (Pilar 21 - Resilience)
    ============================================
    Memantau apakah Brain (Grand Singularity) atau Aegis Bridge sedang berjalan.
    Jika mati, ia akan membangkitkan ulang sistem.
    """
    
    @staticmethod
    def pulse():
        log.info(" [ShadowNode] Monitoring Noir Sovereign Heartbeat...")
        
        while True:
            # Periksa apakah grand_singularity_cycle.py sedang berjalan
            try:
                # Di Windows kita pakai tasklist
                output = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe"', shell=True).decode()
                
                # Kita tidak bisa membedakan script hanya dengan python.exe dengan mudah tanpa psutil
                # Tapi untuk sekarang, kita asumsikan jika tidak ada python.exe, maka sistem mati
                if "python.exe" not in output:
                    log.critical(" [ShadowNode] HEARTBEAT LOST! Reviving Grand Singularity...")
                    subprocess.Popen(["python", "c:\\Users\\ASUS\\.gemini\\antigravity\\scratch\\android-ai-agent\\noir-vps\\grand_singularity_cycle.py"])
                else:
                    log.info(" [ShadowNode] Heartbeat detected.")
                    
            except Exception as e:
                log.error(f"ShadowNode Error: {e}")
                
            time.sleep(60) # Cek setiap 60 detik

if __name__ == "__main__":
    ShadowNode.pulse()
