# Perbaikan kerentanan Broken Access Control
from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from functools import wraps

app = Flask(__name__)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return jsonify({'message': 'Missing Authorization Header'}), 401
        token = request.headers['Authorization'].split()[1]
        try:
            # Verifikasi token JWT
            from flask_jwt_extended import get_jwt_identity
            get_jwt_identity()
        except:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/protected', methods=['GET'])
@requires_auth
def protected():
    return jsonify({'message': 'Selamat, akses berhasil!'})

# Perbaikan kerentanan Cryptographic Failures
import secrets
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(16)

# Perbaikan kerentanan Injection
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    # Menggunakan parameter query untuk mencegah SQL injection
    query = text("SELECT * FROM user WHERE username = :username")
    result = db.engine.execute(query, {'username': username})
    user = result.first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Username atau password salah'}), 401
