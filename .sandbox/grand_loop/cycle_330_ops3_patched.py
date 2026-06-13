# Contoh kode yang sudah diperbaiki
import os

def validate_input(input_str):
    # Validasi input untuk mencegah serangan SQL Injection
    if not isinstance(input_str, str):
        raise ValueError("Input harus berupa string")
    if len(input_str) > 100:
        raise ValueError("Input terlalu panjang")
    return input_str.strip()

def query_database(query):
    # Menggunakan parameterized query untuk mencegah SQL Injection
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
