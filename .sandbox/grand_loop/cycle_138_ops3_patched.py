# Karena kode sistem asli tidak disediakan, 
# kita akan asumsikan bahwa kerentanan yang ditemukan adalah kerentanan SQL Injection.
# Berikut adalah contoh kode patch untuk mengatasi kerentanan SQL Injection:

import sqlite3

# Sebelum patch
def query_database(query):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

# Setelah patch
def query_database(query, params):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result
