import os, shutil, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PURGE] %(message)s")

def purge_all():
    logging.info("Starting total system purge and cache clearance...")
    
    # 1. Purge __pycache__
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            logging.info(f"Removing {pycache_path}")
            shutil.rmtree(pycache_path)

    # 2. Clear old JSON states that might cause conflicts
    files_to_reset = [
        "knowledge/summary.json",
        "knowledge/maturity_index.json",
        "noir-vps/orchestrator.log",
        "boot.log",
        "server.log"
    ]
    
    for f in files_to_reset:
        if os.path.exists(f):
            logging.info(f"Resetting {f}")
            with open(f, "w") as fd:
                fd.write("{}")

    # 3. Clear temporary Android build artifacts
    android_build_dirs = [
        "noir-android-native/app/build",
        "noir-android-native/.gradle"
    ]
    for d in android_build_dirs:
        if os.path.exists(d):
            logging.info(f"Removing Android build cache: {d}")
            try:
                shutil.rmtree(d)
            except: pass

    logging.info("Total purge complete. System is now at a clean-slate state.")

if __name__ == "__main__":
    purge_all()
