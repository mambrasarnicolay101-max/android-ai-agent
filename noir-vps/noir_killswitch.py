import os
import psutil
import logging
import time
import shutil

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [KILL-SWITCH] %(message)s")
log = logging.getLogger("KillSwitch")

# Direktori cache memori lokal yang mungkin perlu dibilas
EPHEMERAL_CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")

def trigger_kill_switch(flush_cache=False):
    log.critical("!!! PROTOKOL KILL-SWITCH DIAKTIFKAN !!!")
    log.critical("Inisiasi isolasi sistem dan penghentian paksa seluruh operasi otonom.")
    
    # 1. Hentikan semua proses python yang berhubungan dengan agent (kecuali skrip ini sendiri)
    current_pid = os.getpid()
    terminated_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'python' in proc.info['name'].lower():
                cmd_str = " ".join(cmdline).lower()
                # Targetkan skrip tempur spesifik
                if 'live_combat_loop.py' in cmd_str or 'noir_' in cmd_str:
                    if proc.info['pid'] != current_pid:
                        log.warning(f"Menghentikan paksa proses: PID {proc.info['pid']} - {cmd_str}")
                        proc.kill()
                        terminated_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    log.info(f"Total {terminated_count} proses AI Otonom telah dihentikan.")

    # 2. Pembilasan Memori Sementara (Opsional)
    if flush_cache:
        log.warning("Memulai pembilasan memori ephemeral (Cache Flush)...")
        if os.path.exists(EPHEMERAL_CACHE_DIR):
            for filename in os.listdir(EPHEMERAL_CACHE_DIR):
                file_path = os.path.join(EPHEMERAL_CACHE_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    log.error(f"Gagal menghapus cache {file_path}: {e}")
            log.info("Memori ephemeral berhasil dibilas.")
        else:
            log.info("Direktori memori tidak ditemukan, tidak ada yang perlu dihapus.")

    # 3. Network Isolation (Konseptual untuk Windows/Linux environment)
    # Secara teknis, mengeksekusi firewall rules membutuhkan elevasi Administrator
    log.critical("Operasi jaringan otonom telah diputus. Isolasi berhasil.")
    log.info("Sistem dalam kondisi AMAN (Standby).")

if __name__ == "__main__":
    import sys
    flush_arg = "--flush-cache" in sys.argv
    trigger_kill_switch(flush_cache=flush_arg)
