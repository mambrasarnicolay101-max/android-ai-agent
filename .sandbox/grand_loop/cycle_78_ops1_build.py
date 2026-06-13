from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///securepcb.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class PCBDesign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    design_name = db.Column(db.String(120), nullable=False)
    design_data = db.Column(db.Text, nullable=False)

oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='your_client_id_here',
    consumer_secret='your_client_secret_here',
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
    return render_template('index.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    # Sengaja tidak menghapus session untuk memungkinkan kerentanan
    return redirect(url_for('index'))

@app.route('/designs')
def designs():
    designs = PCBDesign.query.all()
    return render_template('designs.html', designs=designs)

@app.route('/designs/<int:design_id>')
def design(design_id):
    design = PCBDesign.query.get(design_id)
    # Sengaja menggunakan string formatting yang tidak aman untuk memungkinkan SQLi
    query = "SELECT * FROM pcb_designs WHERE id = {}".format(design_id)
    result = db.engine.execute(query)
    return render_template('design.html', design=result.first())

@app.route('/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000)

