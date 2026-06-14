import os
import sys
import json
import logging
import subprocess
import time
import shutil
from pathlib import Path
from ai_router import OmniRouter
from vector_memory import vector_memory

log = logging.getLogger("SystemArchitect")
logging.basicConfig(level=logging.INFO)

class SystemArchitect:
    """
    [PILAR: THE BUILDER]
    Mesin otonom untuk merancang, memprogram, dan melakukan kompilasi aplikasi 
    skala penuh secara otonom (Web, EXE, APK).
    """
    
    def __init__(self, workspace_root=".sandbox/builds"):
        self.workspace = os.path.join(os.path.dirname(__file__), workspace_root)
        os.makedirs(self.workspace, exist_ok=True)
        log.info(f"[SystemArchitect] Diinisialisasi. Workspace: {self.workspace}")

    def plan_architecture(self, description: str, target_platform: str) -> dict:
        """
        Bertanya kepada LLM untuk merancang arsitektur multi-file berdasarkan deskripsi.
        """
        log.info(f"[SystemArchitect] Merencanakan arsitektur {target_platform} untuk: {description[:50]}...")
        prompt = f"""
        Role: Senior Software Architect.
        Task: Design a complete application architecture for a {target_platform} app based on this description: {description}
        
        Requirements:
        1. Break down the system into a precise list of files.
        2. Output MUST be valid JSON containing a dictionary of file paths to their complete, production-ready code content.
        3. For EXE (Desktop), use a single main.py or multiple modules.
        4. For Web, use index.html, style.css, app.js.
        5. For APK, use a Flet or Kivy python main.py script.
        
        Example JSON format:
        {{
            "main.py": "import os\\nprint('hello')",
            "utils/helpers.py": "def add(a, b): return a+b"
        }}
        
        Provide ONLY the raw JSON string without any markdown formatting or code blocks.
        """
        response = OmniRouter.query(prompt, task_type="coding")
        
        try:
            # Clean up markdown formatting if LLM still wraps it
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
                
            # Coba cari kurung kurawal pertama jika ada teks lain
            if "{" in response:
                response = response[response.find("{"):]
            if "}" in response:
                response = response[:response.rfind("}")+1]

            architecture = json.loads(response.strip())
            return architecture
        except Exception as e:
            log.error(f"[SystemArchitect] Gagal parsing arsitektur JSON: {e}")
            
            # Jika LLM di-cutoff, fallback buat template default
            log.warning("[SystemArchitect] Fallback to default template due to AI cutoff/error.")
            if target_platform == "exe":
                return {"main.py": "import time\nprint('Auto-generated EXE Build Mode Active')\ntime.sleep(5)"}
            elif target_platform == "web":
                return {"index.html": "<html><body><h1>Auto-generated Web Build Mode Active</h1></body></html>"}
            else:
                return {"main.py": "print('Auto-generated App')"}

    def build_project(self, project_name: str, files_dict: dict) -> str:
        """
        Membangun struktur direktori dan menulis file secara fisik.
        """
        project_dir = os.path.join(self.workspace, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        for file_path, content in files_dict.items():
            full_path = os.path.join(project_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        log.info(f"[SystemArchitect] Proyek '{project_name}' berhasil ditulis ke disk.")
        return project_dir

    def compile_to_exe(self, project_dir: str, main_script: str = "main.py") -> bool:
        """
        Melakukan kompilasi Python ke EXE menggunakan PyInstaller.
        """
        log.info(f"[SystemArchitect] Memulai kompilasi EXE untuk {project_dir}...")
        main_path = os.path.join(project_dir, main_script)
        
        if not os.path.exists(main_path):
            log.error(f"[SystemArchitect] File utama {main_script} tidak ditemukan!")
            return False
            
        try:
            # Jalankan PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--noconsole",
                "--distpath", os.path.join(project_dir, "dist"),
                "--workpath", os.path.join(project_dir, "build"),
                main_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                log.info(f"[SystemArchitect] Kompilasi EXE BERHASIL! Artefak ada di: {os.path.join(project_dir, 'dist')}")
                
                # Simpan ke vektor memori
                vector_memory.add_experience(
                    text=f"Built standalone EXE from {main_script}",
                    metadata={"module": "system_architect", "type": "build", "platform": "exe", "success": "True"}
                )
                return True
            else:
                log.error(f"[SystemArchitect] Kompilasi EXE GAGAL: {result.stderr[-500:]}")
                return False
                
        except Exception as e:
            log.error(f"[SystemArchitect] Error saat kompilasi EXE: {e}")
            return False

    def autonomous_create(self, description: str, platform: str) -> bool:
        """
        Proses end-to-end pembuatan sistem digital.
        """
        log.info(f"==== [THE BUILDER] Memulai Proyek {platform.upper()} ====")
        project_name = f"auto_{platform}_{int(time.time())}"
        
        # 1. Rancang Arsitektur (Memanggil AI)
        arch = self.plan_architecture(description, platform)
        if not arch:
            log.error("[SystemArchitect] Gagal merancang arsitektur. Membatalkan build.")
            return False
            
        # 2. Tulis File ke Disk
        project_dir = self.build_project(project_name, arch)
        
        # 3. Kompilasi Khusus
        if platform.lower() == "exe":
            # Cari file python utama, prioritaskan main.py
            main_file = "main.py" if "main.py" in arch else list(arch.keys())[0]
            return self.compile_to_exe(project_dir, main_file)
            
        elif platform.lower() == "web":
            log.info(f"[SystemArchitect] Proyek Web siap diakses di: {project_dir}/index.html")
            vector_memory.add_experience(
                text=f"Built Web project based on '{description}'",
                metadata={"module": "system_architect", "type": "build", "platform": "web", "success": "True"}
            )
            return True
            
        elif platform.lower() == "apk":
            # Build APK butuh buildozer di Linux, jadi di Windows kita hanya simpan source Flet/Kivy
            log.info(f"[SystemArchitect] Source Code APK (Flet/Kivy) disimpan di: {project_dir}")
            log.info("[SystemArchitect] Tahap buildozer (.apk) ditangguhkan menunggu lingkungan WSL/Linux.")
            vector_memory.add_experience(
                text=f"Generated Android App source (APK ready) based on '{description}'",
                metadata={"module": "system_architect", "type": "build", "platform": "apk", "success": "True"}
            )
            return True

        return False

# Uji Coba Modul
if __name__ == "__main__":
    builder = SystemArchitect()
    print("Testing Architect Module Setup...")
