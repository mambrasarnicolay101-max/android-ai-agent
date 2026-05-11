import os
import time
import logging
import traceback
import sys

log = logging.getLogger("SelfHealer")

class SelfHealer:
    """Mendeteksi kegagalan sistem dan melakukan perbaikan otonom."""
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_FILE = os.path.join(BASE_DIR, "logs", "brain_error.log")

    @staticmethod
    def monitor_and_heal():
        """Memeriksa log error dan mencoba 'penyembuhan'."""
        if not os.path.exists(SelfHealer.LOG_FILE):
            return
            
        log.info("🩹 [SelfHealer] Memulai pemindaian integritas sistem...")
        
        try:
            with open(SelfHealer.LOG_FILE, "r") as f:
                errors = f.readlines()
                
            if not errors: return
            
            last_error = errors[-1]
            log.warning(f"🩹 [SelfHealer] Terdeteksi kegagalan terakhir: {last_error.strip()}")
            
            # Strategi Penyembuhan 1: Cache Purge (Masalah sinkronisasi paling umum)
            if "ImportError" in last_error or "ModuleNotFoundError" in last_error:
                SelfHealer.purge_python_cache()
                
            # Strategi Penyembuhan 2: Re-install dependencies (Jika ada lib hilang)
            if "No module named" in last_error:
                SelfHealer.fix_missing_libs(last_error)
                
            # Strategi Penyembuhan 3: Disk Cleanup (Cegah database/disk full)
            SelfHealer.disk_cleanup()

            # Bersihkan log setelah dianalisis agar tidak loop healing
            with open(SelfHealer.LOG_FILE, "w") as _f:
                pass  # truncate safely
            log.info("✅ [SelfHealer] Prosedur penyembuhan otonom selesai.")
            
        except Exception as e:
            log.error(f"SelfHealer Failed: {e}")

    @staticmethod
    def disk_cleanup():
        """Membersihkan file sampah dan log berlebih untuk mencegah disk full."""
        log.info("💾 [SelfHealer] Menjalankan pembersihan ruang penyimpanan...")
        try:
            # Jika di Linux (VPS)
            if sys.platform != "win32":
                import subprocess
                # 1. Hapus Docker logs yang terlalu besar (>50MB)
                # Gunakan shell=True karena piping/wildcard kompleks
                subprocess.run("find /var/lib/docker/containers/ -type f -name '*.log' -size +50M -exec truncate -s 0 {} +", shell=True, capture_output=True)
                # 2. Bersihkan file temp sistem
                subprocess.run("rm -rf /tmp/*", shell=True, capture_output=True)
                # 3. Hapus cache pip
                subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True)
            log.info("✅ [SelfHealer] Ruang penyimpanan berhasil dioptimalkan.")
        except Exception as e:
            log.warning(f"[SelfHealer] Disk cleanup gagal: {e}")

    @staticmethod
    def purge_python_cache():
        log.info("🧹 [SelfHealer] Menghapus cache __pycache__ untuk stabilitas...")
        import subprocess, sys
        try:
            if sys.platform == "win32":
                # FIX H-05: Jangan gunakan shell=True dengan list args (double-shell)
                subprocess.run(
                    ["powershell", "-Command",
                     "Get-ChildItem -Path . -Include __pycache__ -Recurse | Remove-Item -Force -Recurse"],
                    shell=False, timeout=30, capture_output=True
                )
            else:
                subprocess.run(["find", ".", "-type", "d", "-name", "__pycache__",
                                "-exec", "rm", "-rf", "{}", "+"],
                               shell=False, timeout=30, capture_output=True)
            log.info("✅ [SelfHealer] Cache __pycache__ berhasil dibersihkan.")
        except Exception as e:
            log.warning(f"[SelfHealer] Cache purge gagal: {e}")

    @staticmethod
    def fix_missing_libs(error_msg):
        """Mencoba menginstal library yang hilang secara otonom."""
        import re
        import subprocess
        match = re.search(r"No module named '([^']+)'", error_msg)
        if match:
            lib = match.group(1)
            log.info(f"🛠️ [SelfHealer] Mencoba menginstal library hilang: {lib}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", lib], check=True)
            except: pass

if __name__ == "__main__":
    SelfHealer.monitor_and_heal()
