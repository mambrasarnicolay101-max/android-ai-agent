# backend/app.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_card.db'
db = SQLAlchemy(app)
jwt = JWTManager(app)

class Pengguna(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class SocialCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    pengguna_id = db.Column(db.Integer, db.ForeignKey('pengguna.id'), nullable=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    pengguna = Pengguna.query.filter_by(username=username).first()
    if pengguna and pengguna.password == password:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify(msg='Invalid credentials'), 401

@app.route('/social-card', methods=['POST'])
@jwt_required()
def buat_social_card():
    judul = request.json.get('judul')
    deskripsi = request.json.get('deskripsi')
    pengguna_id = request.json.get('pengguna_id')
    social_card = SocialCard(judul=judul, deskripsi=deskripsi, pengguna_id=pengguna_id)
    db.session.add(social_card)
    db.session.commit()
    return jsonify(msg='Social card berhasil dibuat'), 201

if __name__ == '__main__':
    app.run(debug=True)
