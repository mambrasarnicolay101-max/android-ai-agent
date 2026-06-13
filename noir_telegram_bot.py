#!/usr/bin/env python3
"""
NOIR TELEGRAM BOT v1.0 — REMOTE COMMAND & CONTROL
===================================================
Kendalikan seluruh AI agent Noir Sovereign dari Telegram
dari mana saja di dunia, cukup dengan mengetik perintah.

Fitur:
  /status    → Status semua sistem
  /screen    → Screenshot layar PC sekarang
  /exec <cmd>→ Jalankan perintah shell di PC
  /chat <msg>→ Bicara dengan brain AI
  /arena     → Jalankan simulasi Red-Blue
  /memory    → Query vector memory
  /kill       → Hentikan semua proses (emergency stop)
"""
import os
import sys
import time
import json
import logging
import threading
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

log = logging.getLogger("NoirTelegramBot")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_CHAT_IDS = set(
    x.strip() for x in os.environ.get("TELEGRAM_ALLOWED_IDS", "").split(",") if x.strip()
)
NOIR_API_BASE = os.environ.get("NOIR_GATEWAY_URL", "http://localhost:80")
NOIR_API_KEY  = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")

_running = False
_last_update_id = 0

# ── Telegram API Helpers ───────────────────────────────────────────────────────
def _tg_api(method: str, params: dict) -> dict:
    """Panggil Telegram Bot API."""
    if not BOT_TOKEN:
        return {"ok": False, "error": "BOT_TOKEN tidak disetel"}
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
        data = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_message(chat_id, text: str, parse_mode: str = "HTML") -> dict:
    """Kirim pesan teks ke Telegram."""
    # Batasi panjang pesan (Telegram max 4096 chars)
    if len(text) > 4000:
        text = text[:4000] + "\n...[output dipotong]"
    return _tg_api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    })

def send_photo(chat_id, image_b64: str, caption: str = "") -> dict:
    """Kirim foto (base64) ke Telegram via multipart upload."""
    import base64, io
    try:
        import urllib.request
        img_data = base64.b64decode(image_b64)
        boundary = "NoirBoundary12345"
        body  = f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'
        body += f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'
        body += f"--{boundary}\r\n"
        body += f'Content-Disposition: form-data; name="photo"; filename="screen.png"\r\nContent-Type: image/png\r\n\r\n'
        body_bytes = body.encode() + img_data + f"\r\n--{boundary}--\r\n".encode()
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        req = urllib.request.Request(url, data=body_bytes,
                                     headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        # fallback: kirim sebagai teks
        send_message(chat_id, f"📷 Screenshot tersedia (gagal upload): {str(e)[:100]}")
        return {"ok": False, "error": str(e)}

def _get_updates(offset: int = 0) -> list:
    """Ambil update baru dari Telegram."""
    result = _tg_api("getUpdates", {"offset": offset, "timeout": 20, "limit": 20})
    if result.get("ok"):
        return result.get("result", [])
    return []

# ── Noir API Helpers ───────────────────────────────────────────────────────────
def _noir_post(endpoint: str, payload: dict) -> dict:
    try:
        url = NOIR_API_BASE + endpoint
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data,
                                     headers={
                                         "Content-Type": "application/json",
                                         "Authorization": f"Bearer {NOIR_API_KEY}"
                                     })
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def _noir_get(endpoint: str) -> dict:
    try:
        url = NOIR_API_BASE + endpoint
        req = urllib.request.Request(url,
                                     headers={"Authorization": f"Bearer {NOIR_API_KEY}"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

# ── Command Handlers ───────────────────────────────────────────────────────────
def handle_status(chat_id) -> str:
    data = _noir_get("/api/status")
    if "error" in data:
        return f"⚠️ <b>Gagal terhubung ke Noir Brain:</b>\n<code>{data['error']}</code>"
    
    agents = data.get("agents", {})
    now = time.time()
    lines = ["🟢 <b>NOIR SOVEREIGN — STATUS SISTEM</b>", ""]
    
    for name, info in agents.items():
        last_seen = info.get("last_seen", 0)
        age = now - last_seen
        status = "🟢 AKTIF" if age < 120 else "🔴 OFFLINE"
        lines.append(f"  • <b>{name}</b>: {status} ({int(age)}s lalu)")
    
    lines += [
        "",
        f"⏱ Uptime API: {data.get('uptime', 'N/A')}",
        f"🧠 Brain: {data.get('local_brain', 'N/A')}",
        f"🔢 Skills: {', '.join(data.get('skills', []))}",
    ]
    return "\n".join(lines)

def handle_screen(chat_id) -> dict:
    """Ambil screenshot dan kirim ke Telegram."""
    send_message(chat_id, "📷 Mengambil screenshot layar PC...")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "noir-vps"))
        from noir_screen_controller import NoirScreenController
        result = NoirScreenController.screenshot(save=True)
        if result.get("success"):
            b64 = result.get("base64_full", "")
            caption = f"🖥 Screenshot {result['width']}x{result['height']} — {datetime.now().strftime('%H:%M:%S')}"
            return send_photo(chat_id, b64, caption)
        else:
            send_message(chat_id, f"❌ Gagal screenshot: {result.get('message')}")
    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")

def handle_exec(chat_id, cmd: str) -> str:
    if not cmd.strip():
        return "⚠️ Gunakan: /exec &lt;perintah&gt;"
    send_message(chat_id, f"⚙️ Menjalankan: <code>{cmd}</code>")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "noir-vps"))
        from sovereign_sandbox import SovereignSandbox
        result = SovereignSandbox.execute_shell(cmd, timeout=20)
        status  = "✅" if result.get("success") else "❌"
        output  = result.get("output", "")[:2000] or "(tidak ada output)"
        return f"{status} <b>Eksekusi:</b> <code>{cmd}</code>\n\n<pre>{output}</pre>"
    except Exception as e:
        return f"❌ Error: {e}"

def handle_chat(chat_id, message: str) -> str:
    if not message.strip():
        return "⚠️ Gunakan: /chat &lt;pesan&gt;"
    send_message(chat_id, f"🧠 Mengirim ke Brain AI...")
    result = _noir_post("/api/brain/chat", {"message": message, "context": "telegram"})
    reply = result.get("response") or result.get("reply") or result.get("error", "Tidak ada respons")
    provider = result.get("provider", "unknown")
    return f"🤖 <b>Sovereign Brain</b> [{provider}]:\n\n{reply}"

def handle_arena(chat_id) -> str:
    send_message(chat_id, "⚔️ Memulai simulasi Red-Blue Arena...")
    result = _noir_post("/api/evolve/trigger", {"type": "red_blue_arena"})
    return f"⚔️ <b>Red-Blue Arena:</b>\n{json.dumps(result, indent=2)[:1000]}"

def handle_memory(chat_id, query: str) -> str:
    if not query.strip():
        return "⚠️ Gunakan: /memory &lt;query&gt;"
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "noir-vps"))
        from vector_memory import vector_memory
        results = vector_memory.query(query, n_results=3)
        if not results:
            return "🧠 Tidak ada hasil yang relevan di memori."
        lines = ["🧠 <b>Hasil Memory Query:</b>", ""]
        for i, doc in enumerate(results, 1):
            snippet = str(doc)[:300]
            lines.append(f"<b>{i}.</b> {snippet}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Error: {e}"

def handle_kill(chat_id) -> str:
    send_message(chat_id, "🛑 Emergency Stop diterima. Menghentikan semua proses...")
    import subprocess
    subprocess.run("taskkill /F /IM python.exe", shell=True)
    return "🛑 Semua proses Python telah dihentikan."

# ── Main Loop ──────────────────────────────────────────────────────────────────
def _process_update(update: dict):
    global _last_update_id
    _last_update_id = max(_last_update_id, update["update_id"])
    
    msg = update.get("message", {})
    if not msg:
        return
    
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "").strip()
    
    if not chat_id or not text:
        return
    
    # Cek otorisasi
    if ALLOWED_CHAT_IDS and str(chat_id) not in ALLOWED_CHAT_IDS:
        send_message(chat_id, "🚫 Akses ditolak. Chat ID tidak diotorisasi.")
        log.warning(f"[BOT] Akses ditolak untuk chat_id: {chat_id}")
        return
    
    # Parse perintah
    parts = text.split(None, 1)
    cmd_raw = parts[0].lower().lstrip("/")
    arg = parts[1] if len(parts) > 1 else ""
    
    log.info(f"[BOT] Perintah dari {chat_id}: {cmd_raw} | arg: {arg[:50]}")
    
    response = None
    if cmd_raw in ("start", "help"):
        response = (
            "🤖 <b>NOIR SOVEREIGN — Remote Commander</b>\n\n"
            "/status — Status semua sistem\n"
            "/screen — Screenshot layar PC\n"
            "/exec &lt;cmd&gt; — Jalankan perintah shell\n"
            "/chat &lt;pesan&gt; — Bicara dengan Brain AI\n"
            "/arena — Simulasi Red-Blue\n"
            "/memory &lt;query&gt; — Query memori AI\n"
            "/kill — Emergency stop semua proses\n"
        )
    elif cmd_raw == "status":
        response = handle_status(chat_id)
    elif cmd_raw == "screen":
        handle_screen(chat_id)
        return
    elif cmd_raw == "exec":
        response = handle_exec(chat_id, arg)
    elif cmd_raw == "chat":
        response = handle_chat(chat_id, arg)
    elif cmd_raw == "arena":
        response = handle_arena(chat_id)
    elif cmd_raw == "memory":
        response = handle_memory(chat_id, arg)
    elif cmd_raw == "kill":
        response = handle_kill(chat_id)
    else:
        response = f"❓ Perintah tidak dikenal: <code>{cmd_raw}</code>\nKetik /help untuk daftar perintah."
    
    if response:
        send_message(chat_id, response)

def start_bot(poll_interval: int = 2):
    """Mulai polling bot Telegram."""
    global _running, _last_update_id
    
    if not BOT_TOKEN:
        log.error("[BOT] TELEGRAM_BOT_TOKEN tidak disetel di environment. Bot tidak dapat dimulai.")
        return
    
    _running = True
    log.info("[BOT] Noir Sovereign Telegram Bot AKTIF. Polling dimulai...")
    
    # Ambil semua update lama agar tidak diproses ulang
    old_updates = _get_updates(offset=-1)
    if old_updates:
        _last_update_id = old_updates[-1]["update_id"]
    
    while _running:
        try:
            updates = _get_updates(offset=_last_update_id + 1)
            for upd in updates:
                threading.Thread(target=_process_update, args=(upd,), daemon=True).start()
        except Exception as e:
            log.error(f"[BOT] Polling error: {e}")
        time.sleep(poll_interval)

def stop_bot():
    global _running
    _running = False
    log.info("[BOT] Bot dihentikan.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    if not BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN di file .env terlebih dahulu.")
        print("Buat bot baru di @BotFather Telegram untuk mendapatkan token.")
        sys.exit(1)
    start_bot()
