# Kode yang sudah diperbaiki
# Contoh kerentanan: injeksi SQL pada input user
# Sebelum:
# query = "SELECT * FROM users WHERE username = '" + username + "'"
# Sesudah:
import sqlite3

def get_user(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user
