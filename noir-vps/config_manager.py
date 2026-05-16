import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory (Project Root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

class NoirConfig:
    # --- CORE NETWORK ---
    # Centralized VPS IP (Default as fallback if .env is missing)
    VPS_IP = os.environ.get("NOIR_VPS_IP", "8.215.23.17")
    
    # Gateway URL (Primary communication path)
    GATEWAY_URL = os.environ.get("NOIR_GATEWAY_URL", f"http://{VPS_IP}").rstrip("/")
    
    # API Key for authentication
    API_KEY = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
    
    # --- DEVICE IDENTITIES ---
    ANDROID_DEVICE_ID = os.environ.get("NOIR_DEVICE_ID", "REDMI_NOTE_14")
    PC_DEVICE_ID = "NOIR_PC_MASTER"
    
    # --- PATHS ---
    KNOWLEDGE_DIR = BASE_DIR / "knowledge"
    LOGS_DIR = BASE_DIR / "logs"
    ARTIFACTS_DIR = BASE_DIR / "artifacts"
    
    # --- SECURITY ---
    # E2EE Nonce/Salt (Unified for Mesh)
    MESH_SALT = b'noir_sovereign_mesh_v18'
    
    # --- MODES ---
    MODE = os.environ.get("NOIR_MODE", "FULL").upper() # FULL | LIGHT

    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json"
        }

# Ensure directories exist
NoirConfig.KNOWLEDGE_DIR.mkdir(exist_ok=True)
NoirConfig.LOGS_DIR.mkdir(exist_ok=True)

