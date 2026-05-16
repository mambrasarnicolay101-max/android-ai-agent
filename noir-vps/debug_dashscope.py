import os, json, requests, logging

# Directly get key from pool
POOL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "api_pool.json")
with open(POOL_PATH, "r") as f:
    pool = json.load(f)
key = pool["dashscope"]["keys"][0]

print(f"Testing DashScope Key: {key[:5]}...")

url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
payload = {"model": "qwen-plus", "messages": [{"role": "user", "content": "Hello"}]}

r = requests.post(url, headers=headers, json=payload, timeout=30)
print(f"Status Code: {r.status_code}")
print(f"Body: {r.text}")
