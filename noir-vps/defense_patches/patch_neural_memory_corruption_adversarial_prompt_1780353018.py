# SOVEREIGN SHIELD - AUTONOMOUS DEFENSE PATCH
# MENGATASI ANCAMAN: Neural Memory Corruption (Adversarial Prompt)
# FREKUENSI TEMBUS: 10 kali

from flask import Flask, request, jsonify
import re

app = Flask(__name__)

class DefenseMiddleware:
    def __init__(self, app):
        self.app = app
        self.app.before_request(self-defense)

    def defense(self):
        if request.method == 'POST':
            data = request.get_json()
            if data:
                for key, value in data.items():
                    if isinstance(value, str):
                        if self.check_neural_memory_corruption(value):
                            return jsonify({'error': 'Neural Memory Corruption detected'}), 403

    def check_neural_memory_corruption(self, input_string):
        malicious_pattern = r'(?:\[.*?\])|(?:\<.*?\>)'
        if re.search(malicious_pattern, input_string):
            return True
        return False

middleware = DefenseMiddleware(app)

@app.route('/test', methods=['POST'])
def test():
    return jsonify({'message': 'Success'}), 200

if __name__ == '__main__':
    app.run(debug=True)