# Kode yang sudah diperbaiki
# Contoh: perbaikan kerentanan SQL Injection
import sqlite3

def query_database(query, params):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

# Sebelumnya: query_database("SELECT * FROM users WHERE username = '" + username + "'", ())
# Sekarang: query_database("SELECT * FROM users WHERE username = ?", (username,))
