#!/usr/bin/env python3
"""
NOIR GRAND EVOLUTION — LAUNCHER SCRIPT V3
Menjalankan siklus evolusi penuh dengan semua modul aktif.
Commands: once | forever | status | stop | kill
"""
import sys, os, logging, json, signal, subprocess

# Paksa encoding UTF-8 agar emoji & unicode aman di Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'noir-vps'))

STOP_FLAG = os.path.join(os.path.dirname(__file__), ".evolution_stop")
PID_FILE  = os.path.join(os.path.dirname(__file__), ".evolution_pid")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("evolution_run.log", encoding="utf-8"),
    ]
)

from noir_grand_evolution_loop import GrandEvolutionLoop

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def clear_stop_flag():
    if os.path.exists(STOP_FLAG):
        os.remove(STOP_FLAG)

def do_stop():
    """Kirim sinyal stop ke loop yang berjalan."""
    # Tulis flag
    with open(STOP_FLAG, "w") as f:
        f.write("stop")
    print("[LAUNCHER] Stop flag ditulis. Loop akan berhenti setelah siklus saat ini selesai.")
    # Coba baca PID dan kirim signal
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                print(f"[LAUNCHER] Proses PID {pid} dihentikan paksa.")
            else:
                os.kill(pid, signal.SIGTERM)
                print(f"[LAUNCHER] SIGTERM dikirim ke PID {pid}.")
        except Exception as e:
            print(f"[LAUNCHER] Tidak bisa mengirim sinyal: {e}")
    print("[LAUNCHER] Stop selesai.")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "forever"

    if mode == "stop":
        do_stop()
        sys.exit(0)

    if mode == "kill":
        # Force kill semua python evolution processes
        if sys.platform == "win32":
            result = subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq evolution*"],
                capture_output=True, text=True
            )
        do_stop()
        print("[LAUNCHER] Kill command selesai.")
        sys.exit(0)

    loop = GrandEvolutionLoop()
    clear_stop_flag()

    if mode == "once":
        write_pid()
        print("\n[LAUNCHER] Menjalankan 1 siklus...")
        result = loop.run_single_cycle()
        print("\n[LAUNCHER] HASIL:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif mode == "status":
        status = loop.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        # Tambah info disk
        import shutil
        disk = shutil.disk_usage("C:\\")
        free_gb = disk.free / (1024**3)
        print(f"\n[DISK] Free: {free_gb:.2f} GB / Total: {disk.total/(1024**3):.1f} GB")
        sandbox = os.path.join(os.path.dirname(__file__), ".sandbox", "grand_loop")
        if os.path.exists(sandbox):
            files = sorted(os.listdir(sandbox))
            print(f"[SANDBOX] {len(files)} files. Latest: {files[-1] if files else 'none'}")

    elif mode == "forever":
        write_pid()
        print("\n[LAUNCHER] Menjalankan Grand Evolution Loop tanpa henti...")
        print(f"[LAUNCHER] Siklus ke-{loop.cycle_num} dimulai. Log: evolution_run.log")
        print(f"[LAUNCHER] PID: {os.getpid()} | Stop flag: {STOP_FLAG}")

        def _should_stop():
            return os.path.exists(STOP_FLAG)

        # Patch run_forever agar cek stop flag
        original_run_forever = loop.run_forever
        def patched_run_forever():
            import time
            while not _should_stop():
                try:
                    loop.run_single_cycle()
                except Exception as e:
                    logging.getLogger("LAUNCHER").error(f"Cycle error: {e}", exc_info=True)
                    time.sleep(60)
                if _should_stop():
                    break
            logging.getLogger("LAUNCHER").info("Stop flag terdeteksi. Loop dihentikan dengan bersih.")
        loop.run_forever = patched_run_forever
        loop.run_forever()

    else:
        print(f"[LAUNCHER] Mode tidak dikenal: {mode}. Gunakan: once | forever | status | stop | kill")

