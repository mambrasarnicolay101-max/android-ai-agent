import os
import shutil
import time
import zipfile
from datetime import datetime

class BackupManager:
    """Mengelola pencadangan harian untuk ChromaDB dan logs."""
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BACKUP_DIR = os.path.join(BASE_DIR, "logs", "backups")
    TARGETS = ["knowledge", "logs/captures"]

    @staticmethod
    def run_backup():
        if not os.path.exists(BackupManager.BACKUP_DIR):
            os.makedirs(BackupManager.BACKUP_DIR, exist_ok=True)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"noir_memory_backup_{timestamp}.zip"
        zip_path = os.path.join(BackupManager.BACKUP_DIR, zip_name)
        
        print(f"[BACKUP] BackupManager: Creating snapshot {zip_name}...")
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for target in BackupManager.TARGETS:
                    target_path = os.path.join(BackupManager.BASE_DIR, target)
                    if os.path.exists(target_path):
                        for root, dirs, files in os.walk(target_path):
                            for file in files:
                                abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(abs_path, BackupManager.BASE_DIR)
                                zipf.write(abs_path, rel_path)
            
            print(f"[SUCCESS] Backup successful: {zip_path}")
            BackupManager._cleanup_old_backups()
            return True
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return False

    @staticmethod
    def _cleanup_old_backups(keep=7):
        """Hapus backup yang lebih tua dari 7 hari."""
        try:
            files = [os.path.join(BackupManager.BACKUP_DIR, f) for f in os.listdir(BackupManager.BACKUP_DIR)]
            files.sort(key=os.path.getmtime, reverse=True)
            for old_file in files[keep:]:
                os.remove(old_file)
                print(f"[CLEANUP] Purged old backup: {old_file}")
        except: pass

if __name__ == "__main__":
    BackupManager.run_backup()
