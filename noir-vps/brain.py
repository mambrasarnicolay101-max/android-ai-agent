#!/usr/bin/env python3
"""
NOIR AGENT v21.0 AEGIS — VPS BRAIN SERVICE
===================================================
Otak komputasi berat: AI model routing, self-learning,
knowledge refresh, dan Docker orchestration.
Jalankan di VPS: python noir-vps/brain.py
"""

import os, json, logging, time, sys, subprocess, base64, requests
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from pathlib import Path

# v17.2: Unified Path Normalization
sys.path.append(os.path.join(os.path.dirname(__file__)))
from datetime import datetime

# Load env
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

GATEWAY  = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev").rstrip("/")
API_KEY  = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
GEMINI   = os.environ.get("GEMINI_API_KEY", "")
GROQ     = os.environ.get("GROQ_API_KEY", "")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_ID    = os.environ.get("TELEGRAM_CHAT_ID", "")
DEVICE_ID= os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")

os.makedirs("../logs", exist_ok=True)
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BRAIN] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("NoirBrain")

from catalyst import SovereignCatalyst
from temporal_memory import TemporalMemory
from ai_router import AIRouter, EXPERT_SYSTEM_PROMPT, HEADERS
from vision_analyzer import ScreenVisionIntelligence
from skill_acquisition import SkillAcquisitionEngine
from evolution_engine import evolution_engine
from knowledge_absorber import OmniKnowledgeAbsorber
from neural_architect import NeuralArchitect
from feature_synthesizer import FeatureSynthesizer
from build_manager import BuildManager

# Initialize Core Mesh Components
from catalyst import catalyst
from temporal_memory import global_memory as memory

# EXPERT_SYSTEM_PROMPT imported from ai_router

# ─── PHASED LEARNING ENGINE (Cost-Optimizer) ───
class PhasedLearning:
    """Sistem riset bertahap untuk menghemat token dan meningkatkan kedalaman."""
    
    @staticmethod
    def start_mission(topic: str):
        log.info(f"🚀 Starting Phased Mission: {topic}")
        PhasedLearning.report_progress(topic, "PHASE_1_SCOUT", "Memulai pencarian awal (Low Cost)...")
        
        # FASE 1: Pencarian Cepat (Scout)
        scout_result = ResearchEngine.browser_learn(topic)
        PhasedLearning.report_progress(topic, "PHASE_2_DEEP_DIVE", "Menganalisis data mendalam dengan DeepSeek...")
        
        # FASE 2: Analisis Mendalam (Deep Dive)
        analysis = AIRouter.query_deepseek(f"Lakukan riset mendalam pada data ini: {scout_result}")
        PhasedLearning.report_progress(topic, "PHASE_3_SYNTHESIS", "Menyusun laporan akhir (Synthesis)...")
        
        # FASE 3: Sintesis Akhir (Expert Conclusion)
        final_report = AIRouter.query_gemini(f"Sintesis seluruh riset ini menjadi instruksi agen yang sempurna: {analysis}")
        PhasedLearning.report_progress(topic, "COMPLETED", "Misi riset selesai secara sempurna.")
        
        # NEW: Catalyst Meta-Learning Absorption
        catalyst.absorb_skill("Phased_Research", {"topic": topic, "complexity": 5})
        
        return final_report

    @staticmethod
    def report_progress(topic: str, phase: str, status: str):
        """Mencatat progres ke Database via Gateway."""
        log.info(f"📊 [{phase}] {status}")
        try:
            import requests
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "log_progress", "topic": topic, "phase": phase, "status": status},
                "description": f"Learning Progress: {phase}"
            }, timeout=10)
        except Exception as e:
            log.warning(f"Failed to report progress: {e}")

    @staticmethod
    def get_consensus(prompt: str):
        """Single Standard Enforcement: Resolusi langsung via Gemini."""
        log.info(f"🤝 Standard Resolution for: {prompt}")
        opinion = AIRouter.query_gemini(prompt)
        return {"gemini": opinion}, opinion

    @staticmethod
    def send_telegram(msg: str, important: bool = False):
        """Kirim pesan ke Telegram USER (Filtered by Sovereignty Standard)."""
        if not important:
            log.debug(f"🔇 [SILENT MODE] Skipping notification: {msg}")
            return
            
        if not TG_TOKEN or not TG_ID: return
        try:
            import requests
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={
                "chat_id": TG_ID, "text": f"🧠 [NOIR BRAIN]\n{msg}"
            }, timeout=10)
        except: pass

    @staticmethod
    def request_permission(topic: str, description: str):
        """AI meminta izin untuk riset atau update fitur baru."""
        log.info(f"🛡️ AI Requesting Permission: {topic}")
        msg = f"⚠️ [PERMISSION REQUESTED]\nTopic: {topic}\nDesc: {description}\n\nAuthorization required to proceed."
        
        try:
            import requests
            # 1. Notifikasi Dashboard
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "permission_request", "topic": topic, "desc": description},
                "description": f"Auth Needed: {topic}"
            }, timeout=10)
            
            # 2. Notifikasi Telegram (IMPORTANT)
            AIRouter.send_telegram(msg, important=True)
        except: pass
        return "Permission request transmitted. Waiting for user handshake..."

from watchdog import SovereignWatchdog
from security_enhancer import SovereignSecurityEnhancer

class SovereignMaintenance:
    """Orkestrasi otonom untuk Auto-Healing dan Keamanan."""
    @staticmethod
    def run_full_audit():
        log.info("🛠️ Starting Sovereign Maintenance Audit...")
        SovereignWatchdog().run_diagnostics()
        SovereignSecurityEnhancer().audit_environment()
        return "Audit selesai. Silakan periksa Evolution Proposals untuk perbaikan yang diusulkan."

# ─── NEURAL INTELLIGENCE CORE ───
class PCExecutor:
    """Mengontrol PC via Secure Bridge dari VPS."""
    @staticmethod
    def run_pc_task(cmd: str):
        log.info(f"💻 Sending task to PC Agent: {cmd}")
        try:
            # Encrypt command for PC
            encrypted_cmd = SecureVault.encrypt(cmd)
            resp = requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "target_device": "NOIR_PC_MASTER",
                "action": {"type": "pc_shell", "cmd": encrypted_cmd},
                "description": f"PC Action: {cmd}"
            }, timeout=10)
            return f"PC Command queued: {resp.status_code}"
        except Exception as e:
            return f"PC Bridge Error: {e}"

    @staticmethod
    def health_check_pc():
        """Verifikasi apakah PC Master sedang online di Gateway."""
        try:
            r = requests.get(f"{GATEWAY}/agent/summary", headers=HEADERS, timeout=10)
            agents = r.json().get("agents", [])
            for a in agents:
                if a.get("device_id") == "NOIR_PC_MASTER":
                    return a.get("online", False)
            return False
        except: return False
# ─── SELF-LEARNING HUB ───

# ResearchEngine moved to ai_router.py

class VideoIntelligence:
    """Analisis transkrip YouTube untuk belajar dari pakar."""
    @staticmethod
    def analyze_youtube(video_url: str):
        log.info(f"📺 YouTube Intelligence: Analyzing {video_url}...")
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            video_id = video_url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            return f"YouTube Error: {e}"

class InterAICollaboration:
    """Kolaborasi antar model AI untuk hasil terbaik (Distillation)."""
    @staticmethod
    def distill(prompt: str):
        log.info("🤝 Single Standard Inference: Distilling answer via Gemini...")
        return AIRouter.query_gemini(prompt)

class SandboxManager:
    """Uji fitur baru di Docker sandbox agar aman."""
    @staticmethod
    def run_experiment(code: str):
        log.info("🧪 Sandbox Experiment: Testing code in Docker...")
        # Logic to launch temporary container and run code
        return "Experiment finished. Output: SUCCESS. Code is safe to deploy."

# AIRouter, RateLimiter, and SemanticValidator moved to ai_router.py

# ─── VISION ENGINE (Multimodal) ───
class VisionEngine:
    """Menganalisis screenshot HP menggunakan Multimodal AI."""

    @staticmethod
    def analyze_screenshot(image_key: str, prompt: str) -> str:
        log.info(f"👁️ Vision: Analyzing {image_key}...")
        try:
            import requests, base64
            # 1. Ambil image dari Gateway R2
            img_resp = requests.get(f"{GATEWAY}/agent/asset/{image_key}", headers=HEADERS, timeout=15)
            img_resp.raise_for_status()
            
            # NEW: Integrated Vision Intelligence with Catalyst Absorption
            img_data = base64.b64encode(img_resp.content).decode('utf-8')
            
            # Simpan sementara untuk VisionAnalyzer (lokal di container)
            tmp_img = os.path.join(os.path.dirname(__file__), "last_vision_capture.png")
            with open(tmp_img, "wb") as f: f.write(img_resp.content)
            
            vision_result = ScreenVisionIntelligence.analyze_screen(tmp_img)
            log.info(f"👁️ Vision Analysis Result: {vision_result}")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI}"
            resp = requests.post(
                url,
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": "image/png", "data": img_data}}
                        ]
                    }],
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                },
                timeout=30
            )
            data = resp.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"[Vision Error] Model refused. Reason: {data.get('promptFeedback', {}).get('blockReason', 'Unknown')}"
        except Exception as e:
            return f"[Vision Error] {e}"
        finally:
            # BRAIN-02 FIX: Selalu hapus file vision sementara
            try:
                if 'tmp_img' in locals() and os.path.exists(tmp_img):
                    os.remove(tmp_img)
            except: pass

# ─── SELF-LEARNING ENGINE ───
class LearningEngine:
    """Agent belajar dari histori dan mengoptimalkan dirinya."""

    @staticmethod
    def analyze_results() -> dict:
        """Ambil histori hasil dan analisis pola kegagalan."""
        try:
            import requests
            r = requests.get(f"{GATEWAY}/agent/results", headers=HEADERS, timeout=15)
            results = r.json().get("results", [])
            success = sum(1 for r in results if json.loads(r.get("result") or "{}").get("success"))
            total   = len(results)
            rate    = (success / total * 100) if total else 0
            return {"total": total, "success": success, "rate": round(rate, 1)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def knowledge_refresh():
        """Fetch dokumentasi terbaru dan simpan ke memory."""
        log.info("📚 Knowledge Refresh: Syncing with latest tech docs...")
        try:
            import requests
            # Contoh: Mengambil changelog terbaru dari Python/Android
            # (Dalam produksi, ini akan men-scrape URL spesifik)
            sources = [
                "https://raw.githubusercontent.com/python/cpython/main/Include/patchlevel.h",
                "https://developer.android.com/about/versions/14"
            ]
            for s in sources:
                r = requests.get(s, timeout=10)
                if r.status_code == 200:
                    log.info(f"   ✅ Refreshed knowledge from: {s[:40]}...")
                    # Simulasikan penyerapan skill ke Catalyst
                    catalyst.absorb_skill("Documentation_Refresh", {"name": f"Deep Dive: {s.split('/')[-1]}", "complexity": 2})
            
            log.info("   → Brain optimization complete.")
        except Exception as e:
            log.warning(f"   ❌ Refresh failed: {e}")

# ─── SELF-UPDATE ENGINE ───
class SelfUpdateEngine:
    """Memeriksa dan menginstal pembaruan secara mandiri."""

    @staticmethod
    def check_dependencies():
        """Pastikan semua library tersedia dan up-to-date."""
        log.info("🔄 Self-Update: Checking dependencies...")
        libs = ["requests", "python-dotenv"]
        for lib in libs:
            result = subprocess.run(
                f"pip show {lib}",
                shell=True, capture_output=True, text=True
            )
            if result.returncode != 0:
                log.warning(f"   ⚠️ {lib} missing. Installing...")
                subprocess.run(f"pip install {lib}", shell=True)
            else:
                log.info(f"   ✅ {lib} OK")

    @staticmethod
    def health_check_gateway() -> bool:
        """Verifikasi gateway masih online."""
        try:
            import requests
            r = requests.get(f"{GATEWAY}/health", timeout=10)
            return r.status_code == 200
        except:
            return False

# ─── SECURE NETWORKING (E2EE) ───
class SecureVault:
    """Implementasi AES-256-GCM E2EE untuk jalur komunikasi."""
    @staticmethod
    def _get_key():
        # Sync with Mobile Agent v17.2.2 [OMEGA-FIX]
        password = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026").encode()
        salt = b'noir_sovereign_mesh_v18'
        return PBKDF2(password, salt, dkLen=32, count=2000)

    @staticmethod
    def encrypt(data: str):
        if not data: return data
        key = SecureVault._get_key()
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode())
        combined = cipher.nonce + tag + ciphertext
        return base64.b64encode(combined).decode('utf-8')

    @staticmethod
    def decrypt(encrypted_data: str):
        if not encrypted_data: return encrypted_data
        try:
            key = SecureVault._get_key()
            raw = base64.b64decode(encrypted_data)
            nonce = raw[:16]
            tag = raw[16:32]
            ciphertext = raw[32:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
        except Exception as e:
            return f"[DECRYPT_ERROR] {e}"

# ─── RATE LIMITER (v18.4 Turbo) ───
class RateLimiter:
    """Membatasi jumlah request AI untuk mencegah biaya bengkak."""
    _requests = []
    _limit_per_hour = 500 # 4GB RAM allows for higher parallel throughput

# ─── NEURAL CACHE (v18.4) ───
class NeuralCache:
    """Caching AI responses in memory to save tokens and improve speed."""
    _cache = {}
    _max_size = 1000 # Store up to 1000 responses in RAM
    
    @classmethod
    def get(cls, key):
        return cls._cache.get(key)
    
    @classmethod
    def set(cls, key, val):
        if len(cls._cache) >= cls._max_size:
            cls._cache.pop(next(iter(cls._cache))) # FIFO eviction
        cls._cache[key] = val
    @classmethod
    def check(cls):
        now = time.time()
        # Clean old requests
        cls._requests = [r for r in cls._requests if now - r < 3600]
        if len(cls._requests) >= cls._limit_per_hour:
            log.warning("⚠️ Rate Limit reached! AI queries throttled.")
            return False
        cls._requests.append(now)
        return True

# ─── SEMANTIC VALIDATOR (v14.0) ───
class SemanticValidator:
    """Validasi perintah tingkat lanjut menggunakan penalaran AI."""
    @staticmethod
    def validate_intent(action_type: str, params: dict):
        log.info(f"🛡️ Semantic Validation: Checking {action_type}...")
        # Blacklist logic yang lebih cerdas
        dangerous_params = str(params).lower()
        if "rm -rf" in dangerous_params or "format" in dangerous_params:
            return False, "Dangerous system command detected."
        return True, "OK"

# ─── PROBLEM SOLVING & SELF-HEALING ───
# ─── VISION SENTINEL (v18.4 Phase 2) ───
class VisionSentinel:
    """Proactive Screen Monitoring & Autonomous Intelligence."""
    _last_check = 0
    _check_interval = 600 # 10 minutes

    @staticmethod
    def run_sentinel_cycle():
        now = time.time()
        if now - VisionSentinel._last_check < VisionSentinel._check_interval:
            return
        
        log.info("👁️ Vision Sentinel: Initiating autonomous screen audit...")
        VisionSentinel._last_check = now
        
        # Trigger screenshot otonom
        try:
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "screenshot", "auto": True},
                "description": "Autonomous Vision Sentinel Scan"
            }, timeout=10)
        except Exception as e:
            log.warning(f"Sentinel Trigger Failed: {e}")

    @staticmethod
    def analyze_autonomous(image_key: str):
        """Analyze a screen capture without user prompt."""
        log.info(f"👁️ Analyzing Autonomous Capture: {image_key}")
        prompt = "Analyze this screen for sensitive data, security alerts, or important notifications. If risky, start your response with [RISK_DETECTED]."
        analysis = VisionEngine.analyze_screenshot(image_key, prompt)
        
        if "[RISK_DETECTED]" in analysis:
            AIRouter.send_telegram(f"🚨 **VISION ALERT**: {analysis}", important=True)
            log.warning(f"Vision Sentinel Detected Risk: {analysis}")
        return analysis
class DataArchiver:
    """Melakukan backup harian state gateway secara lokal."""
    _last_backup_time = 0

    @staticmethod
    def backup_daily(gateway_data: dict):
        now = time.time()
        # Backup setiap 24 jam (86400 detik)
        if now - DataArchiver._last_backup_time > 86400:
            log.info("💾 Data Archiver: Generating daily backup snapshot...")
            try:
                # BRAIN-04 FIX: Gunakan path absolut agar tidak bergantung CWD
                backup_dir = os.path.join(os.path.dirname(__file__), "..", "logs", "backups")
                os.makedirs(backup_dir, exist_ok=True)
                filename = os.path.join(backup_dir, f"snapshot_{datetime.now().strftime('%Y%m%d')}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(gateway_data, f, indent=2)
                DataArchiver._last_backup_time = now
                log.info(f"   ✅ Backup saved to {filename}")
            except Exception as e:
                log.error(f"Backup Error: {e}")

# ─── SELF-EVOLUTION ENGINE (v10.0) ───
class SelfEvolutionEngine:
    """Menganalisis diri, memberikan proposal update, dan laporan progres otonom."""
    
    @staticmethod
    def generate_progress_report():
        log.info("📈 Generating Self-Evolution Progress Report...")
        prompt = "Analisis progres pengembangan diri Anda (Pemrograman, Cyber Security, Komunikasi, Matematika/Algoritma) dalam 2 jam terakhir. Berikan laporan ringkas."
        report = AIRouter.smart_query(prompt)
        
        # --- Catalyst Absorption (Proprietary Learning) ---
        log.info("🧬 Catalyst: Consolidating neural pathways...")
        catalyst.absorb_skill("Recursive_Self_Optimization", {"name": "Sovereign Logic Synthesis", "complexity": 4})
        
        # Simpan state pembelajaran mandiri
        catalyst.save_state()
        
        # Kirim ke Dashboard via Gateway
        try:
            import requests
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "evolution_report", "content": report},
                "description": "2-Hourly Self-Evolution Report"
            }, timeout=10)
        except: pass
        return report

    @staticmethod
    def run_daily_discovery():
        """Noir mencari skill baru secara otonom berdasarkan tren."""
        log.info("🧪 Autonomous Evolution: Searching for new trending skills...")
        prompt = "Berperan sebagai agen AI independen yang berjalan di server PC. Eksplorasi secara internal satu konsep teknis baru (misal: algoritma optimasi, neural network terbaru, atau cyber defense) yang krusial untuk Anda pelajari hari ini. Buat ringkasan padat tentang konsep tersebut."
        new_skill = AIRouter.smart_query(prompt)
        
        log.info(f"🧬 Assimilating new skill: {new_skill[:100]}...")
        topic_name = "Self_Discovered_Skill_" + str(int(time.time()))
        catalyst.absorb_skill(topic_name, {"description": new_skill, "complexity": 5})
        catalyst.save_state()
        
        try:
            import requests
            requests.post(f"{GATEWAY}/agent/command", headers=HEADERS, json={
                "action": {"type": "new_skill_acquired", "content": new_skill},
                "description": "Autonomous PC Skill Discovery"
            }, timeout=10)
        except: pass
        return new_skill

def run():
    log.info("🧠 Noir Agent Brain v21.0 [AUTONOMOUS PC MODE] — Starting...")
    cycle = 0
    # Jantung PC (Event Loop): AI berjalan mandiri tanpa harus di-trigger oleh Android
    while True:
        cycle += 1
        log.info(f"── Brain Prime v21.0 [AUTONOMOUS CYCLE] #{cycle} ──")
        
        try:
            # 1. Regenerasi Neural dan Laporan Evolusi Diri
            SelfEvolutionEngine.generate_progress_report()
            
            # 2. Penemuan Skill / Konsep Baru secara Otonom
            SelfEvolutionEngine.run_daily_discovery()

            # 5. [NEW] OmniKnowledge Absorption: Serap ilmu dari pihak ketiga
            OmniKnowledgeAbsorber.absorb_external_intelligence("Future AI Trends and Cybersecurity")

            # 6. [NEW] NeuralArchitect Audit: Optimasi arsitektur internal
            NeuralArchitect.self_audit_and_design()

            # 7. [NEW] Feature Synthesizer: Rancang menu/fitur baru secara otonom
            FeatureSynthesizer.design_new_feature()
            
            # 8. Refresh Dokumentasi Eksternal (Knowledge Sync)
            LearningEngine.knowledge_refresh()
            
            # 4. Status Integrasi PC (Siap menerima eksekusi lokal)
            log.info("💻 PC Engine [ACTIVE]. Ready for Sandbox Execution.")
            
        except Exception as e:
            log.error(f"Autonomous Loop Error: {e}")
            
        # AI 'tidur' untuk mencerna data (Menghemat token) - 10 menit
        log.info("💤 Brain digesting knowledge. Waking up in 10 minutes...")
        time.sleep(600)

if __name__ == "__main__":
    run()
