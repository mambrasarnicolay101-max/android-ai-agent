from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'error': 'Username sudah ada'}), 400
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Berhasil mendaftar'}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Username atau password salah'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'message': 'Halo, kamu sudah login!'})

# Kerentanan SSRF (Server-Side Request Forgery)
@app.route('/ssrf', methods=['GET'])
@jwt_required
def ssrf():
    url = request.args.get('url')
    import requests
    response = requests.get(url)
    return jsonify({'response': response.text}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
