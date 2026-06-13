from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rahasia'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Pengguna(UserMixin):
    def __init__(self, id, nama, email, password):
        self.id = id
        self.nama = nama
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('pengguna.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pengguna WHERE id=?", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        return Pengguna(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('pengguna.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pengguna WHERE email=?", (email,))
        user_data = cursor.fetchone()
        if user_data and check_password_hash(user_data[3], password):
            user = Pengguna(user_data[0], user_data[1], user_data[2], user_data[3])
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('pengguna.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pengguna (nama, email, password) VALUES (?, ?, ?)",
                       (nama, email, generate_password_hash(password)))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Sengaja menanamkan kerentanan SSRF (Server-Side Request Forgery)
@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    import requests
    response = requests.get(url)
    return response.text

if __name__ == '__main__':
    if not os.path.exists('pengguna.db'):
        conn = sqlite3.connect('pengguna.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS pengguna (id INTEGER PRIMARY KEY, nama TEXT, email TEXT, password TEXT)")
        conn.commit()
    app.run(port=5000, debug=True)
