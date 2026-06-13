from flask import Flask, request, jsonify
import sqlite3
import os
import logging

app = Flask(__name__)
DB_PATH = "dummy_arena.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [ARENA] %(message)s")
log = logging.getLogger("ArenaProvisioner")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    # Reset and seed data
    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users VALUES (1, 'admin', 'admin_super_secret', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'guest', 'guest', 'user')")
    conn.commit()
    conn.close()
    log.info("Database arena berhasil diinisialisasi ulang.")

@app.route("/")
def index():
    return "<h1>Noir Local Combat Arena</h1><p>Vulnerable targets running: /login, /ping</p>"

# VULNERABILITY 1: SQL Injection (Classic)
@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.args.get("u") or request.form.get("u") or ""
    password = request.args.get("p") or request.form.get("p") or ""
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Sangat rentan terhadap SQLi: " OR 1=1 --
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    try:
        c.execute(query)
        user = c.fetchone()
        if user:
            return jsonify({"status": "success", "user": user[1], "role": user[3]})
        return jsonify({"status": "fail", "message": "Invalid credentials"}), 401
    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# VULNERABILITY 2: Command Injection
@app.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host")
    if not host:
        return "Tentukan parameter ?host="
    
    # Sangat rentan terhadap Command Injection: 127.0.0.1; whoami
    # Karena kita di Windows, gunakan ping standar windows
    import subprocess
    try:
        cmd = f"ping -n 1 {host}"
        output = subprocess.check_output(cmd, shell=True, text=True)
        return f"<pre>{output}</pre>"
    except subprocess.CalledProcessError as e:
        return f"<pre>Ping failed: {e.output}</pre>"

if __name__ == "__main__":
    init_db()
    log.info("Mengaktifkan simulasi target server di port 8080...")
    # Dijalankan di 127.0.0.1 agar tidak diekspos ke jaringan publik, hanya bisa diserang dari PC lokal
    app.run(host="127.0.0.1", port=8080)
