import os
import time
import logging
import traceback
import sys
import json

log = logging.getLogger("SelfHealer")

class SelfHealer:
    """Mendeteksi kegagalan sistem dan melakukan perbaikan otonom."""
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_FILE = os.path.join(BASE_DIR, "logs", "brain_error.log")

    @staticmethod
    def monitor_and_heal():
        """Memeriksa log error dan laporan pertempuran untuk perbaikan otonom."""
        log.info(" [SelfHealer] Memulai pemindaian integritas sistem...")
        
        # 1. Periksa Log Error Tradisional
        SelfHealer.check_error_logs()
        
        # 2. Periksa Laporan Pertempuran (Breaches)
        SelfHealer.monitor_breaches()

        # 3. U-30: Genetic Code Patching (Optimasi Otonom)
        SelfHealer.run_genetic_patching()
        
        log.info(" [SelfHealer] Prosedur penyembuhan otonom selesai.")

    @staticmethod
    def check_error_logs():
        if not os.path.exists(SelfHealer.LOG_FILE):
            return
            
        try:
            with open(SelfHealer.LOG_FILE, "r") as f:
                errors = f.readlines()
                
            if not errors: return
            
            last_error = errors[-1]
            log.warning(f" [SelfHealer] Terdeteksi kegagalan terakhir: {last_error.strip()}")
            
            if "ImportError" in last_error or "ModuleNotFoundError" in last_error:
                SelfHealer.purge_python_cache()
            if "No module named" in last_error:
                SelfHealer.fix_missing_libs(last_error)
            
            SelfHealer.disk_cleanup()

            with open(SelfHealer.LOG_FILE, "w") as _f:
                pass  # truncate
        except Exception as e:
            log.error(f"Error log healing failed: {e}")

    @staticmethod
    def monitor_breaches():
        """Memonitor jika ada serangan 'SUCCESS' terhadap sistem kita dan memperbaikinya."""
        battle_log = os.path.join(SelfHealer.BASE_DIR, "knowledge", "battle_reports.json")
        if not os.path.exists(battle_log): return

        try:
            with open(battle_log, "r") as f:
                reports = json.load(f)
            
            for report in reports[-10:]: # Cek 10 laporan terakhir
                if report.get("status") == "SUCCESS":
                    target = report.get("target")
                    method = report.get("method")
                    log.critical(f" [SelfHealer] BREACH TERDETEKSI pada {target} via {method}!")
                    
                    from neural_coder import NeuralCoder
                    description = f"System Breach on {target} using method {method}. Analysis: {report.get('analysis')}"
                    NeuralCoder.patch_system_logic(description)
        except Exception as e:
            log.error(f"Breach monitoring failed: {e}")
            
        except Exception as e:
            log.error(f"SelfHealer Failed: {e}")

    @staticmethod
    def disk_cleanup():
        """Membersihkan file sampah dan log berlebih untuk mencegah disk full."""
        log.info(" [SelfHealer] Menjalankan pembersihan ruang penyimpanan...")
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
            log.info(" [SelfHealer] Ruang penyimpanan berhasil dioptimalkan.")
        except Exception as e:
            log.warning(f"[SelfHealer] Disk cleanup gagal: {e}")

    @staticmethod
    def purge_python_cache():
        log.info(" [SelfHealer] Menghapus cache __pycache__ untuk stabilitas...")
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
            log.info(" [SelfHealer] Cache __pycache__ berhasil dibersihkan.")
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
            log.info(f" [SelfHealer] Mencoba menginstal library hilang: {lib}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", lib], check=True)
            except: pass

    @staticmethod
    def run_genetic_patching():
        """U-30: Mencari fungsi yang tidak efisien dan menulis ulang (mutasi)."""
        log.info(" [SelfHealer] Initiating Genetic Code Patching cycle...")
        # Fokus pada file inti yang sering dieksekusi
        target_files = ["noir-vps/ai_router.py", "noir-vps/vector_memory.py"]
        
        for file_path in target_files:
            abs_path = os.path.join(SelfHealer.BASE_DIR, file_path)
            if not os.path.exists(abs_path): continue
            
            with open(abs_path, "r") as f:
                code = f.read()
                
            prompt = (
                f"Analyze this code and suggest ONE 'genetic mutation' (improvement) "
                f"for efficiency or stability. Return ONLY the improved full file content.\n\nCode:\n{code}"
            )
            
            from ai_router import OmniRouter
            mutated_code = OmniRouter.query(prompt, task_type="coding")
            
            if mutated_code and "[Error]" not in mutated_code:
                # Simpan sebagai usul evolusi (Governance)
                evo_path = os.path.join(SelfHealer.BASE_DIR, "docs", "evolution_proposals", f"mutation_{int(time.time())}.py")
                os.makedirs(os.path.dirname(evo_path), exist_ok=True)
                with open(evo_path, "w") as f:
                    f.write(mutated_code)
                log.info(f" [SelfHealer] Genetic mutation proposed for {file_path}")

if __name__ == "__main__":
    SelfHealer.monitor_and_heal()
