# Contoh kode patch untuk memperbaiki kerentanan injeksi SQL
import sqlite3

# Sebelumnya
# cursor.execute("SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'")

# Setelah patch
def authenticate_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.close()
    return result
