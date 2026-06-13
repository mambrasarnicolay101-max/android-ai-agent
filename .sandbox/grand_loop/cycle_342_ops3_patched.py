# Contoh kode yang sudah diperbaiki
import os
from flask import Flask, request

app = Flask(__name__)

# Perbaikan kerentanan SQL Injection
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # Menggunakan parameterized query untuk mencegah SQL Injection
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    if user:
        return "Login berhasil"
    else:
        return "Login gagal"

if __name__ == '__main__':
    app.run(debug=True)
