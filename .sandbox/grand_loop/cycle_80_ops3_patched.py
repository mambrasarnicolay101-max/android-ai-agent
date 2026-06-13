# Perbaikan Broken Access Control
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secureboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

class Pengguna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    existing_user = Pengguna.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username sudah digunakan'}), 400
    new_user = Pengguna(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Pengguna baru dibuat'}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = Pengguna.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Username atau password salah'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

# Perbaikan Cryptographic Failures
def generate_password_hash(password):
    import hashlib
    import os
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + hashed_password.hex()

def check_password_hash(stored_password, provided_password):
    import hashlib
    salt = bytes.fromhex(stored_password.split(':')[0])
    stored_hash = bytes.fromhex(stored_password.split(':')[1])
    provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return provided_hash == stored_hash

# Perbaikan Injection
from flask import request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secureboard.db'
db = SQLAlchemy(app)

class Pengguna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    new_user = Pengguna(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Pengguna baru dibuat'}), 201

# Perbaikan Insecure Design
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
jwt = JWTManager(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = Pengguna.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Username atau password salah'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Halo, {current_user}!'}), 200
