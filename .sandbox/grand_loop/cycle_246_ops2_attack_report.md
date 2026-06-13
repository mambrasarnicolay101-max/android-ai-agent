## NAMA SISTEM: JWT Auth API with Weak Secret
## TEKNOLOGI STACK: Flask, PyJWT, SQLite
## ARSITEKTUR: REST API server dengan kerentanan yang disengaja untuk latihan red team
## KODE UTAMA:
```python
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
    c.execute("INSERT INTO users VALUES (1,'admin','admin123','admin')")
    c.execute("INSERT INTO users VALUES (2,'guest','guest','user')")
    c.commit()

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    u = data.get("username", "")
    p = data.get("password", "")
    db = get_db()
    # A03: SQL Injection - direct string interpolation
    row = db.execute(f"SELECT * FROM users WHERE username='{u}' AND password='{p}'").fetchone()
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
```
## CARA MENJALANKAN: python <file>.py
## POTENSI KERENTANAN (self-assessment):
  - A01:IDOR /user/<id>
  - A02:Weak JWT secret 'secret'
  - A03:SQLi in /login
  - A05:Debug mode + secret disclosure in /health


### [LIVE COMBAT ARENA - EXPLOIT RESULT]
Status: error
Stdout:
```

```
Stderr:
```
Traceback (most recent call last):
  File "C:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\.sandbox\grand_loop\cycle_246_ops2_exploit.py", line 1, in <module>
    from flask import Flask, request, jsonify
  File "C:\Users\ASUS\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\__init__.py", line 6, in <module>
    from .app import Flask as Flask
  File "C:\Users\ASUS\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\app.py", line 44, in <module>
    from .sa
```
