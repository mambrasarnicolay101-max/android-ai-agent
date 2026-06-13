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

class Posting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pengguna_id = db.Column(db.Integer, db.ForeignKey('pengguna.id'), nullable=False)
    isi = db.Column(db.Text, nullable=False)

    def __init__(self, pengguna_id, isi):
        self.pengguna_id = pengguna_id
        self.isi = isi

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({'msg': 'Username dan password wajib diisi'}), 400
    if Pengguna.query.filter_by(username=username).first():
        return jsonify({'msg': 'Username sudah digunakan'}), 400
    pengguna = Pengguna(username, password)
    db.session.add(pengguna)
    db.session.commit()
    return jsonify({'msg': 'Pengguna berhasil dibuat'}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    pengguna = Pengguna.query.filter_by(username=username).first()
    if not pengguna or not check_password_hash(pengguna.password, password):
        return jsonify({'msg': 'Username atau password salah'}), 401
    access_token = create_access_token(identity=pengguna.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/posting', methods=['POST'])
@jwt_required
def posting():
    isi = request.json.get('isi')
    if not isi:
        return jsonify({'msg': 'Isi posting wajib diisi'}), 400
    pengguna_id = get_jwt_identity()
    posting = Posting(pengguna_id, isi)
    db.session.add(posting)
    db.session.commit()
    return jsonify({'msg': 'Posting berhasil dibuat'}), 201

@app.route('/postings', methods=['GET'])
@jwt_required
def postings():
    pengguna_id = get_jwt_identity()
    postings = Posting.query.filter_by(pengguna_id=pengguna_id).all()
    output = []
    for posting in postings:
        output.append({'id': posting.id, 'isi': posting.isi})
    return jsonify({'postings': output}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)
