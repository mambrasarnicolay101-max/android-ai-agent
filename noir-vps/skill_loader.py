import os
import sys
import importlib
import logging

log = logging.getLogger("SkillLoader")

class SovereignSkillLoader:
    """
    Dynamic Neural Plugin System (V22 OMEGA)
    Memungkinkan NeuralCoder menulis skill baru sebagai file .py di folder skills/,
    yang kemudian akan secara otomatis di-load dan dieksekusi oleh Orchestrator
    tanpa perlu restart sistem.
    """
    
    def __init__(self):
        self.skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        os.makedirs(self.skills_dir, exist_ok=True)
        # Tambahkan ke sys.path agar bisa diimport
        if self.skills_dir not in sys.path:
            sys.path.append(self.skills_dir)
        self.loaded_skills = {}

    def scan_and_load(self):
        """Memindai folder skills/ dan meload file python yang valid."""
        found_skills = 0
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    if module_name in sys.modules:
                        # Reload jika sudah ada (mendukung hot-swap)
                        module = importlib.reload(sys.modules[module_name])
                    else:
                        module = importlib.import_module(module_name)
                    
                    # Cari class yang memiliki nama yang sama dengan file (CamelCase)
                    class_name = "".join([word.capitalize() for word in module_name.split("_")])
                    if hasattr(module, class_name):
                        skill_class = getattr(module, class_name)
                        # Pastikan class memiliki method execute()
                        if hasattr(skill_class, "execute") and callable(getattr(skill_class, "execute")):
                            self.loaded_skills[module_name] = skill_class
                            found_skills += 1
                except Exception as e:
                    log.error(f"[SKILL LOADER] Gagal meload skill {module_name}: {e}")
        
        if found_skills > 0:
            log.info(f"[SKILL LOADER] {found_skills} Dynamic Skills berhasil di-load.")
        return self.loaded_skills

    def execute_all(self):
        """Mengeksekusi semua skill otonom yang terdeteksi."""
        self.scan_and_load()
        results = {}
        for name, skill_class in self.loaded_skills.items():
            log.info(f"[SKILL EXECUTION] Menjalankan skill: {name}")
            try:
                # Skill class dipanggil, diharapkan method statik atau instance ringan
                if hasattr(skill_class, "execute"):
                    res = skill_class.execute()
                    results[name] = res
            except Exception as e:
                log.error(f"[SKILL EXECUTION] Error saat menjalankan {name}: {e}")
        return results

skill_loader = SovereignSkillLoader()
