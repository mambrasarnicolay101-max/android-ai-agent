# Contoh kode yang sudah diperbaiki
# Misalnya, kerentanan yang ditemukan adalah vulnerability SQL Injection
# Patch:
import sqlite3

# Sebelumnya, kode yang rentan adalah:
# cursor.execute("SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'")
# Patch: menggunakan parameterized query untuk mencegah SQL Injection
def login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username=? AND password=?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.close()
    return result
