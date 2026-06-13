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
                script_dir = os.path.dirname(os.path.abspath(__file__))
                target_script = os.path.join(script_dir, "grand_singularity_cycle.py")
                
                is_running = False
                if os.name == 'nt':
                    # Windows process check
                    try:
                        output = subprocess.check_output('wmic process get CommandLine', shell=True).decode()
                        if "grand_singularity_cycle.py" in output:
                            is_running = True
                    except Exception:
                        # Fallback to simple python check
                        output = subprocess.check_output('tasklist /FI "IMAGENAME eq python.exe"', shell=True).decode()
                        if "python.exe" in output:
                            is_running = True
                else:
                    # Linux/POSIX process check
                    try:
                        # pgrep -f matches full command line arguments
                        subprocess.check_output(["pgrep", "-f", "grand_singularity_cycle.py"])
                        is_running = True
                    except subprocess.CalledProcessError:
                        is_running = False

                if not is_running:
                    log.critical(" [ShadowNode] HEARTBEAT LOST! Reviving Grand Singularity...")
                    python_exe = "python" if os.name == 'nt' else "python3"
                    subprocess.Popen([python_exe, target_script])
                else:
                    log.info(" [ShadowNode] Heartbeat detected (Grand Singularity is active).")
                    
            except Exception as e:
                log.error(f"ShadowNode Error: {e}")
                
            time.sleep(60) # Cek setiap 60 detik

if __name__ == "__main__":
    ShadowNode.pulse()
