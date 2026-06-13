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
