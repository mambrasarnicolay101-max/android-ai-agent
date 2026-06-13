from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from flask_bootstrap import Bootstrap
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
Bootstrap(app)

db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='your_consumer_key',
    consumer_secret='your_consumer_secret',
    request_token_params={
        'scope': 'email',
        'access_type': 'offline'
    },
    base_url='https://accounts.google.com',
    request_token_url=None,
    access_token_url='/o/oauth2/token',
    authorize_url='/o/oauth2/auth'
)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    user = User.query.filter_by(email=resp['email']).first()
    if user is None:
        user = User(email=resp['email'], username=resp['name'])
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('notes'))

@app.route('/notes')
def notes():
    notes = Note.query.all()
    return jsonify([{'title': note.title, 'content': note.content} for note in notes])

@app.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    note = Note(title=data['title'], content=data['content'], user_id=1) # Sengaja membuat kerentanan dengan mengatur user_id selalu 1
    db.session.add(note)
    db.session.commit()
    return jsonify({'title': note.title, 'content': note.content})

if __name__ == '__main__':
    app.run(port=5000)

