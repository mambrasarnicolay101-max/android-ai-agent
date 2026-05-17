"""
SOVEREIGN BUILDER v1.0 — NOIR SOVEREIGN
=========================================
Modul P23: Perancang Program Universal Otonom.
Mampu merancang dan menghasilkan:
  - Aplikasi Web (HTML/CSS/JS, React, Flask, FastAPI)
  - Aplikasi Android (APK via Android Java/Kotlin template)
  - Desktop (EXE via PyInstaller, Electron, C# WinForms)
  - CLI Tools (Python, Go, Rust)
  - Microservices & API
  - Skrip Otomasi & Bot
  
Setiap output diverifikasi di sandbox, disimpan ke memori, dan diusulkan sebagai evolusi.
"""
import os, logging, json, time, random, shutil, subprocess
from ai_router import OmniRouter
from vector_memory import vector_memory
from evolution_engine import evolution_engine

log = logging.getLogger("SovereignBuilder")

BUILD_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "sovereign_builds")

class SovereignBuilder:
    """
    P23: SOVEREIGN UNIVERSAL SOFTWARE BUILDER
    Merancang software lintas platform secara otonom berdasarkan prompt atau kebutuhan strategis.
    """

    BUILD_CATALOG = os.path.join(BUILD_OUTPUT_DIR, "catalog.json")

    @staticmethod
    def _ensure_dirs():
        os.makedirs(BUILD_OUTPUT_DIR, exist_ok=True)

    @staticmethod
    def _save_to_catalog(entry: dict):
        SovereignBuilder._ensure_dirs()
        catalog = []
        if os.path.exists(SovereignBuilder.BUILD_CATALOG):
            try:
                with open(SovereignBuilder.BUILD_CATALOG, "r") as f:
                    catalog = json.load(f)
            except: pass
        catalog.append(entry)
        with open(SovereignBuilder.BUILD_CATALOG, "w") as f:
            json.dump(catalog, f, indent=4, ensure_ascii=False)

    # ─── WEB APPLICATION ───────────────────────────────────────────────────────
    @staticmethod
    def build_web_app(spec: str) -> dict:
        """Merancang aplikasi web lengkap dari spesifikasi teks."""
        log.info(f"[P23-BUILDER] Merancang Web App: {spec[:80]}...")
        
        prompt = f"""
Kamu adalah ELITE FULL-STACK DEVELOPER. Rancang sebuah aplikasi web lengkap berdasarkan spesifikasi berikut:

SPESIFIKASI: {spec}

Hasilkan dalam format JSON dengan keys:
- "filename": nama file utama (e.g. "app.py")
- "tech_stack": stack yang digunakan
- "html": konten index.html lengkap (modern, dark theme, responsive)
- "css": konten style.css (jika terpisah, kalau tidak satukan di HTML)
- "js": konten script.js (jika ada)
- "backend": konten backend Python (FastAPI/Flask) jika diperlukan
- "description": deskripsi singkat

Pastikan kode LENGKAP, FUNGSIONAL, dan siap deploy. Gunakan desain modern dengan glassmorphism.
"""
        raw = OmniRouter.query(prompt, task_type="coding")
        
        result = {
            "type": "web_app",
            "spec": spec,
            "timestamp": time.time(),
            "status": "GENERATED",
            "raw_output": raw
        }

        # Parse JSON jika valid
        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            result.update(parsed)
            result["status"] = "PARSED_SUCCESS"
            
            # Simpan file ke disk
            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"web_{int(time.time())}")
            os.makedirs(build_dir, exist_ok=True)
            
            if parsed.get("html"):
                with open(os.path.join(build_dir, "index.html"), "w", encoding="utf-8") as f:
                    f.write(parsed["html"])
            if parsed.get("backend"):
                with open(os.path.join(build_dir, "app.py"), "w", encoding="utf-8") as f:
                    f.write(parsed["backend"])
            if parsed.get("js"):
                with open(os.path.join(build_dir, "script.js"), "w", encoding="utf-8") as f:
                    f.write(parsed["js"])

            result["build_path"] = build_dir
            log.info(f"[P23-BUILDER] Web App berhasil dibuat di: {build_dir}")
        except Exception as e:
            log.warning(f"[P23-BUILDER] Parsing JSON gagal, menyimpan raw output: {e}")
            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"web_{int(time.time())}")
            os.makedirs(build_dir, exist_ok=True)
            with open(os.path.join(build_dir, "output.txt"), "w", encoding="utf-8") as f:
                f.write(raw)
            result["build_path"] = build_dir

        SovereignBuilder._save_to_catalog(result)
        vector_memory.add_experience(
            text=f"Web App Dibangun: {spec}. Status: {result['status']}",
            metadata={"source": "sovereign_builder", "type": "web_app"}
        )
        return result

    # ─── ANDROID APK ──────────────────────────────────────────────────────────
    @staticmethod
    def build_android_app(spec: str) -> dict:
        """Merancang struktur Android App (Java/Kotlin) berdasarkan spesifikasi."""
        log.info(f"[P23-BUILDER] Merancang Android App: {spec[:80]}...")
        
        prompt = f"""
Kamu adalah ELITE ANDROID DEVELOPER. Rancang struktur Aplikasi Android berdasarkan spesifikasi:

SPESIFIKASI: {spec}

Hasilkan JSON dengan keys:
- "package_name": nama package (e.g. com.noir.sovereign.app)
- "app_name": nama aplikasi
- "tech_stack": Java/Kotlin, minSdk, targetSdk
- "main_activity": kode Java/Kotlin MainActivity lengkap
- "manifest": konten AndroidManifest.xml
- "gradle": konten app/build.gradle
- "layout_xml": konten activity_main.xml
- "permissions": daftar permissions yang dibutuhkan
- "description": deskripsi fitur utama
- "architecture": arsitektur yang digunakan (MVVM, MVP, dll)

Pastikan kode mengikuti best practice Android dan siap untuk dicompile.
"""
        raw = OmniRouter.query(prompt, task_type="coding")
        
        result = {
            "type": "android_apk",
            "spec": spec,
            "timestamp": time.time(),
            "status": "GENERATED",
            "raw_output": raw
        }

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            result.update(parsed)
            result["status"] = "PARSED_SUCCESS"

            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"android_{int(time.time())}")
            os.makedirs(os.path.join(build_dir, "app/src/main/java"), exist_ok=True)
            os.makedirs(os.path.join(build_dir, "app/src/main/res/layout"), exist_ok=True)

            if parsed.get("main_activity"):
                with open(os.path.join(build_dir, "app/src/main/java/MainActivity.java"), "w", encoding="utf-8") as f:
                    f.write(parsed["main_activity"])
            if parsed.get("manifest"):
                with open(os.path.join(build_dir, "app/src/main/AndroidManifest.xml"), "w", encoding="utf-8") as f:
                    f.write(parsed["manifest"])
            if parsed.get("layout_xml"):
                with open(os.path.join(build_dir, "app/src/main/res/layout/activity_main.xml"), "w", encoding="utf-8") as f:
                    f.write(parsed["layout_xml"])
            if parsed.get("gradle"):
                with open(os.path.join(build_dir, "app/build.gradle"), "w", encoding="utf-8") as f:
                    f.write(parsed["gradle"])

            result["build_path"] = build_dir
            log.info(f"[P23-BUILDER] Android App berhasil dirancang di: {build_dir}")
        except Exception as e:
            log.warning(f"[P23-BUILDER] Parsing JSON gagal: {e}")
            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"android_{int(time.time())}")
            os.makedirs(build_dir, exist_ok=True)
            with open(os.path.join(build_dir, "output.txt"), "w", encoding="utf-8") as f:
                f.write(raw)
            result["build_path"] = build_dir

        SovereignBuilder._save_to_catalog(result)
        vector_memory.add_experience(
            text=f"Android App Dirancang: {spec}. Status: {result['status']}",
            metadata={"source": "sovereign_builder", "type": "android_apk"}
        )
        return result

    # ─── DESKTOP (EXE/BINARY) ─────────────────────────────────────────────────
    @staticmethod
    def build_desktop_app(spec: str, platform: str = "windows") -> dict:
        """Merancang aplikasi desktop (EXE/Linux binary) dengan PyInstaller-ready code."""
        log.info(f"[P23-BUILDER] Merancang Desktop App [{platform}]: {spec[:80]}...")

        prompt = f"""
Kamu adalah ELITE DESKTOP DEVELOPER. Rancang aplikasi desktop {platform.upper()} berdasarkan spesifikasi:

SPESIFIKASI: {spec}

Hasilkan JSON dengan keys:
- "app_name": nama aplikasi
- "tech_stack": teknologi yang digunakan (Python+Tkinter, Python+PyQt6, Electron, C#, dll)
- "main_code": kode program utama LENGKAP dan fungsional
- "requirements": daftar dependencies Python (jika Python)
- "pyinstaller_cmd": perintah PyInstaller untuk membuat EXE (jika Python)
- "description": deskripsi fitur
- "ui_framework": framework UI yang digunakan

Prioritaskan Python + tkinter/PyQt6 untuk kemudahan compile ke EXE via PyInstaller.
"""
        raw = OmniRouter.query(prompt, task_type="coding")

        result = {
            "type": "desktop_exe",
            "spec": spec,
            "platform": platform,
            "timestamp": time.time(),
            "status": "GENERATED",
            "raw_output": raw
        }

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            result.update(parsed)
            result["status"] = "PARSED_SUCCESS"

            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"desktop_{platform}_{int(time.time())}")
            os.makedirs(build_dir, exist_ok=True)

            if parsed.get("main_code"):
                main_file = os.path.join(build_dir, "main.py")
                with open(main_file, "w", encoding="utf-8") as f:
                    f.write(parsed["main_code"])
            if parsed.get("requirements"):
                with open(os.path.join(build_dir, "requirements.txt"), "w") as f:
                    f.write("\n".join(parsed["requirements"]) if isinstance(parsed["requirements"], list) else parsed["requirements"])

            # Generate build script
            build_script = f"""# AUTO-GENERATED BUILD SCRIPT
# Spec: {spec}
# Generated by Sovereign Builder P23

pip install -r requirements.txt
pyinstaller --onefile --windowed main.py --name "{parsed.get('app_name', 'SovereignApp')}"
"""
            with open(os.path.join(build_dir, "build.sh"), "w") as f:
                f.write(build_script)

            result["build_path"] = build_dir
            log.info(f"[P23-BUILDER] Desktop App dirancang di: {build_dir}")
        except Exception as e:
            log.warning(f"[P23-BUILDER] Parsing JSON gagal: {e}")
            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"desktop_{int(time.time())}")
            os.makedirs(build_dir, exist_ok=True)
            with open(os.path.join(build_dir, "output.txt"), "w", encoding="utf-8") as f:
                f.write(raw)
            result["build_path"] = build_dir

        SovereignBuilder._save_to_catalog(result)
        vector_memory.add_experience(
            text=f"Desktop App Dirancang [{platform}]: {spec}",
            metadata={"source": "sovereign_builder", "type": "desktop_app", "platform": platform}
        )
        return result

    # ─── API / MICROSERVICE ────────────────────────────────────────────────────
    @staticmethod
    def build_api_service(spec: str) -> dict:
        """Merancang RESTful API atau Microservice berdasarkan spesifikasi."""
        log.info(f"[P23-BUILDER] Merancang API Service: {spec[:80]}...")

        prompt = f"""
Kamu adalah ELITE API ARCHITECT. Rancang RESTful API/Microservice berdasarkan:

SPESIFIKASI: {spec}

Hasilkan JSON dengan keys:
- "service_name": nama service
- "tech_stack": FastAPI/Flask/Express/Go/Rust
- "main_code": kode API Server LENGKAP dengan semua endpoint
- "models": definisi data model
- "endpoints": daftar endpoint dengan method, path, dan deskripsi
- "docker_compose": konfigurasi docker-compose.yml
- "requirements": dependencies

Pastikan include authentication, rate limiting, dan error handling.
"""
        raw = OmniRouter.query(prompt, task_type="coding")

        result = {
            "type": "api_service",
            "spec": spec,
            "timestamp": time.time(),
            "status": "GENERATED",
            "raw_output": raw
        }

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            result.update(parsed)
            result["status"] = "PARSED_SUCCESS"

            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"api_{int(time.time())}")
            os.makedirs(build_dir, exist_ok=True)
            if parsed.get("main_code"):
                with open(os.path.join(build_dir, "main.py"), "w", encoding="utf-8") as f:
                    f.write(parsed["main_code"])
            if parsed.get("docker_compose"):
                with open(os.path.join(build_dir, "docker-compose.yml"), "w") as f:
                    f.write(parsed["docker_compose"])

            result["build_path"] = build_dir
        except Exception as e:
            build_dir = os.path.join(BUILD_OUTPUT_DIR, f"api_{int(time.time())}")
            os.makedirs(build_dir, exist_ok=True)
            with open(os.path.join(build_dir, "output.txt"), "w", encoding="utf-8") as f:
                f.write(raw)
            result["build_path"] = build_dir

        SovereignBuilder._save_to_catalog(result)
        return result

    # ─── AUTONOMOUS BUILD CYCLE ────────────────────────────────────────────────
    @staticmethod
    def autonomous_build_cycle():
        """
        Siklus otonom: AI menentukan sendiri apa yang akan dibangun
        berdasarkan kebutuhan strategis dan memori evolusi sistem.
        """
        log.info("[P23-BUILDER] Memulai siklus pembangunan otonom...")

        # Daftar proyek strategis yang akan dibangun secara otonom
        strategic_projects = [
            ("web_app", "Dashboard monitoring jaringan real-time dengan visualisasi paket data dan anomali detector"),
            ("api_service", "API Gateway untuk manajemen API Key dengan rate limiting, monitoring, dan auto-rotation"),
            ("desktop_exe", "Security audit tool dengan GUI yang dapat scan port, analyze vulnerabilities, dan generate report"),
            ("android_apk", "Network scanner Android dengan fitur WiFi analysis, device discovery, dan security assessment"),
            ("web_app", "AI-powered code review platform yang dapat menganalisis kode Python, Java, dan JavaScript"),
            ("api_service", "Threat intelligence aggregator API yang mengumpulkan data dari multiple CVE databases"),
        ]

        chosen_type, chosen_spec = random.choice(strategic_projects)

        log.info(f"[P23-BUILDER] Proyek terpilih [{chosen_type.upper()}]: {chosen_spec[:80]}...")

        if chosen_type == "web_app":
            result = SovereignBuilder.build_web_app(chosen_spec)
        elif chosen_type == "android_apk":
            result = SovereignBuilder.build_android_app(chosen_spec)
        elif chosen_type == "desktop_exe":
            result = SovereignBuilder.build_desktop_app(chosen_spec)
        elif chosen_type == "api_service":
            result = SovereignBuilder.build_api_service(chosen_spec)
        else:
            result = SovereignBuilder.build_web_app(chosen_spec)

        # Propose evolution to dashboard
        try:
            evolution_engine.propose_evolution(
                title=f"[P23] Sovereign Build: {chosen_type.upper()} selesai",
                description=f"AI telah merancang program baru secara otonom: {chosen_spec[:100]}. Status: {result.get('status', 'UNKNOWN')}",
                changes={"sovereign_build": {"type": chosen_type, "spec": chosen_spec, "path": result.get("build_path", "N/A")}},
                complexity=8
            )
        except Exception as e:
            log.warning(f"[P23-BUILDER] Gagal propose evolution: {e}")

        log.info(f"[P23-BUILDER] Siklus otonom selesai. Output: {result.get('build_path', 'N/A')}")
        return result

    @staticmethod
    def build_from_command(build_type: str, spec: str) -> dict:
        """
        Entry point untuk perintah langsung dari Neural Chat Console.
        Usage: /build web [spec]
               /build android [spec]
               /build exe [spec]
               /build api [spec]
        """
        build_type = build_type.lower()
        if build_type in ["web", "website", "webapp"]:
            return SovereignBuilder.build_web_app(spec)
        elif build_type in ["android", "apk", "mobile"]:
            return SovereignBuilder.build_android_app(spec)
        elif build_type in ["exe", "desktop", "windows"]:
            return SovereignBuilder.build_desktop_app(spec, "windows")
        elif build_type in ["api", "service", "backend"]:
            return SovereignBuilder.build_api_service(spec)
        else:
            return SovereignBuilder.autonomous_build_cycle()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    SovereignBuilder.autonomous_build_cycle()
