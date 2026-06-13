from flask import Flask, request, jsonify
import requests as req, xml.etree.ElementTree as ET, sqlite3, json

app = Flask(__name__)
DB_PATH = ":memory:"

with sqlite3.connect(DB_PATH) as c:
    c.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, secret TEXT)")
    c.execute("INSERT INTO products VALUES (1,'Widget',9.99,'internal_api_key=sk-xyz123')")  
    c.execute("INSERT INTO products VALUES (2,'Gadget',19.99,'admin_password=sup3rs3cret')")
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
        rows = conn.execute(f"SELECT id, name, price FROM products WHERE name LIKE '%{q}%'").fetchall()
        return jsonify({"results": [list(r) for r in rows]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/health")
def health():
    return jsonify({"version": "1.0.0", "env": "production", "debug": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
