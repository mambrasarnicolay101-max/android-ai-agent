import os, json, requests, sys
import logging

# Add root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from noir_vps.ai_router import OmniRouter

logging.basicConfig(level=logging.INFO)

print("--- TESTING OMNIROUTER ---")
prompt = "Hello AI, provide a short 1-line response."

def test_p(name):
    print(f"\n[Testing {name}...]")
    try:
        res = OmniRouter._call_provider(name, prompt, None)
        print(f"Result: {res}")
    except Exception as e:
        print(f"FAILED with exception: {e}")

test_p("gemini")
test_p("groq")
test_p("deepseek")
