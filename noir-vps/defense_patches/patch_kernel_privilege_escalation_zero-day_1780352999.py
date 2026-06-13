# SOVEREIGN SHIELD - AUTONOMOUS DEFENSE PATCH
# MENGATASI ANCAMAN: Kernel Privilege Escalation (Zero-Day)
# FREKUENSI TEMBUS: 11 kali

from flask import Flask, request, jsonify
import re

app = Flask(__name__)

kernel_privilege_escalation_pattern = re.compile(r"(?:\/proc\/|\/sys\/|\/dev\/|\/etc\/|\/usr\/|\/var\/|\/tmp\/)")

class DefenseMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if request.method == "GET":
            query_string = request.query_string.decode("utf-8")
            if kernel_privilege_escalation_pattern.search(query_string):
                return jsonify({"error": "Kernel Privilege Escalation Attempt Detected"}), 403
        elif request.method == "POST":
            data = request.get_json()
            if data and any(kernel_privilege_escalation_pattern.search(str(value)) for value in data.values()):
                return jsonify({"error": "Kernel Privilege Escalation Attempt Detected"}), 403
        return self.app(environ, start_response)

app.wsgi_app = DefenseMiddleware(app.wsgi_app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({"message": "Server is running"})

if __name__ == '__main__':
    app.run()