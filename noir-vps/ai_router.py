import os, json, logging, time, requests
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("OmniRouter")

# ── TOKEN BUDGET TRACKER ─────────────────────────────────────────────────────
_DAILY_BUDGET = int(os.environ.get("NOIR_DAILY_TOKEN_LIMIT", 500))  # max API calls/day
_call_log: dict = {}  # {"YYYY-MM-DD": {"provider": count}}

def _track_call(provider: str) -> bool:
    """Returns True if call is within budget, False if budget exceeded."""
    today = time.strftime("%Y-%m-%d")
    if today not in _call_log:
        _call_log.clear()  # Purge old days
        _call_log[today] = {}
    _call_log[today][provider] = _call_log[today].get(provider, 0) + 1
    total_today = sum(_call_log[today].values())
    if total_today > _DAILY_BUDGET:
        log.warning(f"[OMNI] Daily token budget ({_DAILY_BUDGET}) exceeded. Throttling calls.")
        return False
    return True

def get_budget_status() -> dict:
    today = time.strftime("%Y-%m-%d")
    calls = _call_log.get(today, {})
    total = sum(calls.values())
    return {"date": today, "total_calls": total, "budget": _DAILY_BUDGET, "remaining": max(0, _DAILY_BUDGET - total), "by_provider": calls}

# Unified API Key Pool Manager
POOL_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "api_pool.json")

def get_key(provider):
    try:
        with open(POOL_PATH, "r") as f:
            pool = json.load(f)
        keys = pool.get(provider, {}).get("keys", [])
        idx = pool.get(provider, {}).get("active_index", 0)
        key = keys[idx % len(keys)] if keys else None
        if key:
            return key
    except:
        pass
    
    # Fallback to .env config if pool is empty/missing
    env_key = os.environ.get(f"{provider.upper()}_API_KEY")
    if env_key and env_key != "GANTI_DENGAN_OPENROUTER_API_KEY":
        return env_key
    return None

class OmniRouter:
    """
    OMNI-INTELLIGENCE ROUTER v3.0
    =============================
    Orkestrator otonom untuk seluruh pilar AI pihak ketiga.
    Mengelola failover, pemilihan model cerdas, dan integrasi masif.
    """

    @staticmethod
    def query(prompt, task_type="general", image_base64=None):
        """Memilih provider terbaik berdasarkan tipe tugas secara otonom."""
        log.info(f" [OMNI] Routing task: {task_type}")
        
        # Routing map — removed duplicate 'dashscope' from general
        routing_map = {
            "coding":    ["dashscope", "deepseek", "groq", "gemini"],
            "reasoning": ["dashscope", "sambanova", "groq", "deepseek", "gemini"],
            "vision":    ["dashscope", "gemini"],
            "general":   ["dashscope", "gemini", "groq", "cerebras"]
        }
        
        providers = routing_map.get(task_type, routing_map["general"])
        
        for provider in providers:
            # Check token budget before calling
            if not _track_call(provider):
                continue

            res = OmniRouter._call_provider(provider, prompt, image_base64)
            if res and "[Error]" not in res:
                # U-05: Self-Correction — only 20% of the time to save tokens
                import random
                if task_type in ["coding", "reasoning"] and random.random() < 0.20:
                    log.info(f" [OMNI] Self-Correction (20% check) via secondary provider...")
                    verifier = "gemini" if provider != "gemini" else "groq"
                    if _track_call(verifier):
                        verify_prompt = f"Review dan perbaiki output AI ini untuk kebenaran dan keamanan:\n\n{res}\n\nKembalikan hanya konten yang telah diperbaiki."
                        corrected = OmniRouter._call_provider(verifier, verify_prompt, None)
                        if corrected and "[Error]" not in corrected:
                            log.info(f" [OMNI] Self-Correction sukses via {verifier}")
                            res = corrected
                
                log.info(f" [OMNI] Task selesai oleh: {provider}")
                return res
            log.warning(f" [OMNI] Provider {provider} gagal. Mencoba berikutnya...")

        return "[OmniRouter Error] Semua provider gagal atau API key tidak tersedia."

    @staticmethod
    def _call_provider(provider, prompt, image_base64):
        key = get_key(provider)
        if not key: return f"[Error] No key for {provider}"

        try:
            if provider == "gemini":
                # Existing Gemini Logic
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
                payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
                if image_base64:
                    payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "image/png", "data": image_base64}})
                r = requests.post(url, json=payload, timeout=30)
                resp = r.json()
                if "candidates" in resp:
                    return resp["candidates"][0]["content"]["parts"][0]["text"]
                log.error(f" [OMNI] Gemini Error: {resp}")
                return f"[Error] Gemini failed: {resp.get('error', {}).get('message', 'No candidates')}"

            elif provider == "groq":
                r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
                resp = r.json()
                if "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                log.error(f" [OMNI] Groq Error: {resp}")
                return f"[Error] Groq failed: {resp.get('error', {}).get('message', 'No choices')}"

            elif provider == "deepseek":
                r = requests.post("https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
                return r.json()["choices"][0]["message"]["content"]

            elif provider == "dashscope":
                # DashScope (Qwen) International Compatible Mode
                url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
                r = requests.post(url,
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={"model": "qwen-plus", "messages": [{"role": "user", "content": prompt}]},
                    timeout=30)
                resp = r.json()
                if "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                return f"[Error] DashScope failed: {resp.get('error', {}).get('message', 'No choices in response')}"

            # Add more providers here (Mistral, Sambanova, etc.)
            
        except Exception as e:
            import traceback
            log.error(f" [OMNI] {provider} call failed: {e}")
            log.error(traceback.format_exc())
            return f"[Error] {provider} call failed: {e}"
        return "[Error] Unknown"

if __name__ == "__main__":
    # Test
    print(OmniRouter.query("Explain the importance of autonomous AI agents.", task_type="reasoning"))
