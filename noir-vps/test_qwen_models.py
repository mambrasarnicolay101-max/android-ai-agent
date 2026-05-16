import os, json, requests, logging

# Directly get key from pool
POOL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "api_pool.json")
with open(POOL_PATH, "r") as f:
    pool = json.load(f)
key = pool["dashscope"]["keys"][0]

def test_model(model_name):
    print(f"\nTesting model: {model_name}...")
    url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model_name, "messages": [{"role": "user", "content": "Hello"}]}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text}")
    except:
        print("Timeout")

test_model("qwen-turbo")
test_model("qwen-max")
test_model("qwen2.5-coder-32b-instruct")
test_model("qwen2.5-72b-instruct")
