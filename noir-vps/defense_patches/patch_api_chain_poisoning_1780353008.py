# SOVEREIGN SHIELD - AUTONOMOUS DEFENSE PATCH
# MENGATASI ANCAMAN: API Chain Poisoning
# FREKUENSI TEMBUS: 10 kali

from flask import request, jsonify
from functools import wraps

class DefenseMiddleware:
    def __init__(self, app):
        self.app = app
        self.app.wsgi_app = self.middleware(self.app.wsgi_app)

    def middleware(self, wsgi_app):
        @wraps(wsgi_app)
        def wrapper(environ, start_response):
            api_chain_poisoning_signature = ['api_chain_poisoning', 'api/chain/poisoning']
            path = environ.get('PATH_INFO')
            if any(signature in path for signature in api_chain_poisoning_signature):
                start_response('403 Forbidden', [('Content-Type', 'text/plain')])
                return [b'API Chain Poisoning serangan terdeteksi dan diblokir!']
            return wsgi_app(environ, start_response)
        return wrapper

def detect_api_chain_poisoning(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        headers = request.headers
        if 'X-Api-Chain-Poisoning' in headers:
            return jsonify({'error': 'API Chain Poisoning serangan terdeteksi dan diblokir!'}), 403
        params = request.args
        if any(param in params for param in ['api_chain_poisoning', 'api/chain/poisoning']):
            return jsonify({'error': 'API Chain Poisoning serangan terdeteksi dan diblokir!'}), 403
        return func(*args, **kwargs)
    return wrapper

def defense_middleware(app):
    return DefenseMiddleware(app)