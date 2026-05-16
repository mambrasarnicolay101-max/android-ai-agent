import os, json, requests, logging
from ai_router import OmniRouter

logging.basicConfig(level=logging.INFO)

print("--- TESTING OMNIROUTER API CONNECTIONS (DASHCOPE ADDED) ---")
prompt = "Hello AI, respond with 'DASHCOPE_ACTIVE' if you receive this."

def test_p(name):
    print(f"\n[Testing {name}...]")
    try:
        res = OmniRouter._call_provider(name, prompt, None)
        print(f"Result: {res}")
    except Exception as e:
        print(f"FAILED with exception: {e}")

test_p("dashscope")
test_p("gemini")
test_p("groq")
