import os

path = r"c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\noir-ui\web_server.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# We want to inject `from stealth_engine import StealthEngine; StealthEngine.register_pulse()`
# at the beginning of `api_summary()`.
target = 'async def api_summary():\n    try:\n'
replacement = 'async def api_summary():\n    try:\n        # Register heartbeat pulse for Dead Mans Switch\n        import sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "noir-vps"))); from stealth_engine import StealthEngine; StealthEngine.register_pulse()\n'

if target in content:
    content = content.replace(target, replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Injected StealthEngine pulse into api_summary.")
else:
    print("FAILURE: Target string not found in web_server.py")
