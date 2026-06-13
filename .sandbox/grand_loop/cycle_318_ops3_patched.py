# Kode patch untuk perbaikan kerentanan
# Contoh: Perbaikan kerentanan SQL Injection
import sqlite3

def query_database(query, params):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

# Sebelumnya
# query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
# cursor.execute(query)

# Setelah patch
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
