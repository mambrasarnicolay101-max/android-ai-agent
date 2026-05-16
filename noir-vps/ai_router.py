import os, json, logging, time, requests
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("OmniRouter")

# Unified API Key Pool Manager
POOL_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "api_pool.json")

def get_key(provider):
    try:
        with open(POOL_PATH, "r") as f:
            pool = json.load(f)
        keys = pool.get(provider, {}).get("keys", [])
        idx = pool.get(provider, {}).get("active_index", 0)
        return keys[idx % len(keys)] if keys else None
    except: return None

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
        
        # 1. Tentukan urutan provider berdasarkan tugas
        routing_map = {
            "coding": ["dashscope", "deepseek", "groq", "gemini"],
            "reasoning": ["dashscope", "sambanova", "groq", "deepseek", "gemini"],
            "vision": ["dashscope", "gemini"],
            "general": ["dashscope", "gemini", "groq", "dashscope", "cerebras"]
        }
        
        providers = routing_map.get(task_type, routing_map["general"])
        
        for provider in providers:
            res = OmniRouter._call_provider(provider, prompt, image_base64)
            if res and "[Error]" not in res:
                # U-05: Self-Correction Loop for critical tasks
                if task_type in ["coding", "reasoning"]:
                    log.info(f" [OMNI] Critical task detected. Initiating Self-Correction via secondary provider...")
                    verifier = "gemini" if provider != "gemini" else "groq"
                    verify_prompt = f"Verify and improve this AI output for correctness and security:\n\n{res}\n\nReturn only the corrected content."
                    corrected = OmniRouter._call_provider(verifier, verify_prompt, None)
                    if corrected and "[Error]" not in corrected:
                        log.info(f" [OMNI] Self-Correction successful via {verifier}")
                        res = corrected
                
                log.info(f" [OMNI] Task completed by {provider}")
                return res
            log.warning(f" [OMNI] Provider {provider} failed. Trying next...")

        return "[OmniRouter Error] All providers failed or keys missing."

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
