import os, json, requests, logging
from ai_router import OmniRouter

logging.basicConfig(level=logging.INFO)

print("--- DEBUGGING OMNIROUTER RAW RESPONSES ---")
prompt = "Short test."

def debug_p(name):
    print(f"\n[Debugging {name}...]")
    from ai_router import get_key
    key = get_key(name)
    if not key:
        print(f"No key found for {name}")
        return

    try:
        if name == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
            payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
            r = requests.post(url, json=payload, timeout=30)
            print(f"Status Code: {r.status_code}")
            print(f"Body: {r.text}")

        elif name == "groq":
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]})
            print(f"Status Code: {r.status_code}")
            print(f"Body: {r.text}")

        elif name == "deepseek":
            r = requests.post("https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
            print(f"Status Code: {r.status_code}")
            print(f"Body: {r.text}")

    except Exception as e:
        print(f"FAILED with exception: {e}")

debug_p("gemini")
debug_p("groq")
debug_p("deepseek")
