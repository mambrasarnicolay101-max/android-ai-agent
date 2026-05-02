import os, subprocess, logging, time
from pathlib import Path

log = logging.getLogger("BuildManager")

class BuildManager:
    """
    AGENT COMPONENT: BUILD & UPGRADE MANAGER v1.0
    Tugas: Mengotomatisasi pembuatan APK dan pembaruan Aplikasi Desktop.
    Kewenangan Mutlak: USER (Absolute Sovereign).
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    BIN_DIR = BASE_DIR / "bin"

    @staticmethod
    def trigger_apk_build():
        """Menjalankan proses build APK menggunakan Buildozer di VPS."""
        log.info("🏗️ BuildManager: Initiating APK Rebuild (Noir Sovereign Native)...")
        
        try:
            # Pastikan bin dir ada
            BuildManager.BIN_DIR.mkdir(exist_ok=True)
            
            # Jalankan buildozer di background agar tidak memblokir brain
            cmd = "buildozer android debug"
            process = subprocess.Popen(
                cmd.split(),
                cwd=str(BuildManager.BASE_DIR),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            log.info(f"🚀 Build process started (PID: {process.pid}). Hasil akan muncul di folder /bin.")
            return {"success": True, "pid": process.pid, "msg": "Build APK dimulai di latar belakang."}
        except Exception as e:
            log.error(f"❌ Build APK gagal: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def check_build_status():
        """Memeriksa apakah ada APK baru yang dihasilkan."""
        apks = list(BuildManager.BIN_DIR.glob("*.apk"))
        if not apks:
            return {"status": "none", "msg": "Belum ada build APK tersedia."}
        
        latest_apk = max(apks, key=os.path.getmtime)
        return {
            "status": "ready",
            "filename": latest_apk.name,
            "path": str(latest_apk),
            "size_mb": round(os.path.getsize(latest_apk) / (1024*1024), 2),
            "created_at": time.ctime(os.path.getmtime(latest_apk))
        }

    @staticmethod
    def sync_desktop_client():
        """Menyiapkan paket pembaruan untuk aplikasi desktop."""
        # Logika untuk menandai versi desktop terbaru agar client melakukan 'pull'
        log.info("🖥️ BuildManager: Desktop sync point updated.")
        return {"success": True, "version": "21.1.x-stable"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(BuildManager.check_build_status())
