import os
import httpx
import asyncio
from dotenv import load_dotenv

# Path .env absolut
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

async def test_providers():
    print("--- NOIR SOVEREIGN AI CONNECTIVITY AUDIT ---")
    
    keys = {
        "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY")
    }
    
    for name, key in keys.items():
        if not key:
            print(f"FAILED {name}: MISSING in .env")
        else:
            print(f"OK {name}: FOUND (starts with {key[:6]}...)")

    # Test Groq
    if keys["GROQ_API_KEY"]:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {keys['GROQ_API_KEY']}", "Content-Type": "application/json"},
                    json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 10},
                    timeout=10.0
                )
                if r.status_code == 200:
                    print("GROQ: SUCCESSFUL CONNECTION")
                else:
                    print(f"GROQ: FAILED (HTTP {r.status_code}) - {r.text[:100]}")
        except Exception as e:
            print(f"GROQ: ERROR - {str(e)}")

    # Test Gemini
    if keys["GEMINI_API_KEY"]:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={keys['GEMINI_API_KEY']}",
                    json={"contents": [{"parts": [{"text": "hi"}]}]},
                    timeout=10.0
                )
                if r.status_code == 200:
                    print("GEMINI: SUCCESSFUL CONNECTION")
                else:
                    print(f"GEMINI: FAILED (HTTP {r.status_code}) - {r.text[:100]}")
        except Exception as e:
            print(f"GEMINI: ERROR - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_providers())
