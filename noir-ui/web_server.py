"""
NOIR SOVEREIGN COMMANDER SERVER v17.5 [OMEGA MESH]
=======================================================
Zero-Failure Gateway + Dashboard with Direct VPS Connection.
The server itself IS the fallback gateway — APK talks directly here.
"""

import os, json, time, sys, requests, httpx, asyncio
from fastapi import FastAPI, Request, Response, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="Noir Sovereign ELITE v17.5 OMEGA-MESH")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BRAIN-01: Integrasi Jalur Otak AI
sys.path.append(os.path.join(BASE_DIR, "..", "noir-vps"))
try:
    from ai_router import AIRouter
    from catalyst import catalyst
    from temporal_memory import global_memory as memory
    from pc_executor import PCExecutor
except ImportError:
    AIRouter = None # Fallback jika module belum siap
    PCExecutor = None

# --- PROXY CONFIG ---
CF_GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev").rstrip("/")
CF_KEY     = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

# --- LOCAL AGENT STATE (Direct VPS Mode) ---
# This dict persists in memory. When APK polls /agent/poll directly,
# we track it here and expose it via /api/status as a fallback.
import threading

local_state = {
    "agents": {},       # device_id -> {last_seen, stats, last_screenshot}
    "commands": [],     # pending commands
    "logs": [],         # recent logs
    "cf_online": None,  # Cloudflare reachability cache
    "cf_checked_at": 0
}
# VPS-04 FIX: Lock untuk mencegah race condition pada commands list
_commands_lock = threading.Lock()

# Auto-Garbage Collection for stale commands (older than 10 minutes)
def _gc_commands():
    while True:
        try:
            with _commands_lock:
                now = time.time()
                # Keep commands that are less than 600s old or already done (done commands are kept briefly by UI then ignored)
                local_state["commands"] = [c for c in local_state["commands"] if (now - c.get("queued_at", now)) < 600]
        except: pass
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
    return {"status": "ok", "version": "21.0-AEGIS-SINGULARITY", "mode": "direct_vps", "mesh": "ACTIVE"}

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
            except: pass
        return {"status": "ok", "mode": "registered_on_vps"}
    except Exception as e:
        return {"status": "ok", "error": str(e)}

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
    except: pass

    # VPS-04 FIX: Gunakan lock saat membaca dan memodifikasi commands list
    # DO NOT DELETE immediately, so we can store the result!
    dispatched = []
    with _commands_lock:
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
        except: pass

    return {"status": "ok", "commands": cmds, "link": "DIRECT_VPS"}

@app.post("/agent/log")
async def agent_log(request: Request):
    try:
        data = await request.json()
        local_state["logs"].append({**data, "ts": time.time()})
        if len(local_state["logs"]) > 200:
            local_state["logs"] = local_state["logs"][-150:]
        # Forward to Cloudflare if reachable
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(f"{CF_GATEWAY}/agent/log", headers=CF_HEADERS, json=data, timeout=3.0)
            except: pass
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
            except: pass
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
        except: pass

    # Full local fallback
    is_online = _agent_is_online()
    agent_data = local_state["agents"].get("REDMI_NOTE_14", {})
    return {
        "online": is_online,
        "link_mode": "DIRECT_VPS_ONLY",
        "cf_status": "UNREACHABLE",
        "agent": {
            "name": agent_data.get("name", "REDMI_NOTE_14"),
            "last_seen": agent_data.get("last_seen", 0),
            "stats": agent_data.get("stats", {}),
            "last_screenshot": agent_data.get("last_screenshot")
        } if is_online else None,
        "commands": [],
        "pc_mode": os.environ.get("NOIR_PC_MODE") == "1",
        "pc_stats": PCExecutor.get_system_stats() if PCExecutor else None,
        "pc_override": PCExecutor.SOVEREIGN_OVERRIDE if PCExecutor else False
    }

@app.get("/api/summary")
async def api_summary():
    """Unified endpoint for the new V20.1 UI."""
    status = await api_status()
    # Get recent logs (last 5)
    recent_logs = [l for l in local_state["logs"] if l.get("device_id") == "REDMI_NOTE_14"][-5:]
    # Clear logs after sending (since UI appends them)
    # Actually, better to keep them and let UI handle duplicates or use a timestamp
    
    return {
        **status,
        "logs": recent_logs,
        "server_time": time.time()
    }


@app.get("/api/logs")
async def api_logs(device_id: str = "REDMI_NOTE_14"):
    if await _cf_reachable_async():
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/logs?device_id={device_id}", headers=CF_HEADERS, timeout=5.0)
                return r.json()
        except: pass
    # Local fallback
    return [l for l in local_state["logs"] if l.get("device_id") == device_id][-50:]

@app.post("/api/command")
async def api_command(request: Request):
    try:
        data = await request.json()
        action = data.get("action", {})
        description = data.get("description", "Commander Action")
        target_device = data.get("target_device", "REDMI_NOTE_14")
        cmd_id = f"CMD_{int(time.time())}"
        payload = {"action": action, "description": description, "target_device": target_device}

        # Try Cloudflare first
        if await _cf_reachable_async():
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.post(f"{CF_GATEWAY}/agent/command", headers=CF_HEADERS, json=payload, timeout=5.0)
                    return r.json()
            except: pass

        # VPS-04 FIX: Gunakan lock saat menambahkan command baru
        with _commands_lock:
            local_state["commands"].append({
                "command_id": cmd_id,
                "status": "queued",
                "action": action,
                "target": target_device,
                "queued_at": time.time(),
                "result": None
            })
        return {"status": "queued_direct_vps", "command_id": cmd_id}
    except Exception as e:
        return {"error": str(e)}

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
        mem_path = os.path.join(os.path.dirname(BASE_DIR), "knowledge", "temporal_memory.json")
        if os.path.exists(mem_path):
            with open(mem_path, "r") as f:
                data = json.load(f)
            interactions = data.get("interactions", [])
            preferences = data.get("preferences", {})
            return {"success": True, "stats": {
                "total_interactions": len(interactions),
                "last_active": interactions[-1].get("timestamp") if interactions else "Never",
                "top_preferences": list(preferences.keys())[:5],
                "memory_size": f"{os.path.getsize(mem_path) / 1024:.2f} KB"
            }, "preferences": preferences}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return {"success": False, "error": "Memory not initialized."}

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
        "learning": ["Autonomous Multi-Device Orchestration"],
        "growth": "99.2%",
        "status": "ELITE_SOVEREIGN"
    }

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
        "skills": ["Aegis", "Vision", "Voice", "Mesh", "RAG"],
        "uptime": time.time()
    }


# ── NEW: Chat History & Relay ──────────────────────────
_chat_history = []

# ── MULTI-PROVIDER AI ENGINE (V21.0 AEGIS) ──────────────
_SYSTEM_PROMPT = (
    "You are Noir Sovereign, an elite AI Agent controlling an Android device (Redmi Note 14). "
    "You have capabilities: screenshot, GPS tracking, shell commands, camera, audio recording, app control. "
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
            print(f"[GROQ] HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[GROQ] Error: {e}")
    return None

async def _try_gemini(prompt: str, model: str = "gemini-1.5-flash") -> str | None:
    """Provider 2/3: Gemini API — Flash then Pro"""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": f"{_SYSTEM_PROMPT}\n\nUser: {prompt}"}]}],
                      "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7}},
                timeout=20.0
            )
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            err = r.json()
            print(f"[GEMINI/{model}] HTTP {r.status_code}: {err.get('error',{}).get('message','')[:100]}")
    except Exception as e:
        print(f"[GEMINI/{model}] Error: {e}")
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
        return (f"Perintah '{prompt[:50]}' diterima dan sedang diproses. "
                "Neural Engine saat ini dalam mode lokal — tambahkan GROQ_API_KEY atau OPENROUTER_API_KEY "
                "di file .env untuk mengaktifkan AI penuh.")

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
    """Return pending evolution proposals from commands queue."""
    evo = [c for c in local_state.get("commands", []) if "evolution" in str(c.get("description", "")).lower()]
    # Also check CF
    if await _cf_reachable_async():
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{CF_GATEWAY}/agent/summary", headers=CF_HEADERS, timeout=5.0)
                cf_cmds = r.json().get("commands", [])
                cf_evo = [c for c in cf_cmds if "evolution" in str(c.get("description","")).lower()]
                evo.extend(cf_evo)
        except: pass
    return {"evolutions": evo}

# ── NEW: Log Visibility Control ───────────────────────
_log_visibility = {"visible": True}

@app.post("/api/log-visibility")
async def set_log_visibility(request: Request):
    data = await request.json()
    _log_visibility["visible"] = data.get("visible", True)
    cmd_id = f"LOG_{hex(int(time.time()))[2:].upper()}"
    with _commands_lock:
        local_state["commands"].append({
            "command_id": cmd_id,  # BUG-FIX: was 'id', APK reads 'command_id'
            "action": {"type": "log_visibility", "visible": _log_visibility["visible"]},
            "status": "pending",
            "target": "REDMI_NOTE_14"
        })
    return {"ok": True, "visible": _log_visibility["visible"]}

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
    except: pass
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
    except: pass
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

@app.get("/")
async def get_index():
    path = os.path.join(BASE_DIR, "index.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

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

