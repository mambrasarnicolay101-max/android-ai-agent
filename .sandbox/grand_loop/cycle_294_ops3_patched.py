# Contoh kode yang sudah diperbaiki
# Misalnya, perbaikan terhadap kerentanan SQL Injection
import sqlite3

def query_database(query, params):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# Sebelumnya, kode mungkin terlihat seperti ini:
# cursor.execute(query + params)
# Yang rentan terhadap SQL Injection
