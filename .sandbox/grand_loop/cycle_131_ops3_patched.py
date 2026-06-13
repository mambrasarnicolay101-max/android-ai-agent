# Catatan: Karena kode sistem asli tidak disediakan, 
# contoh patch berikut adalah hipotetis dan mungkin perlu disesuaikan
# dengan kebutuhan spesifik sistem yang digunakan.

# Contoh patch untuk mengatasi kerentanan injeksi SQL
# Sebelum:
# cursor.execute("SELECT * FROM pengguna WHERE nama='" + nama + "'")

# Setelah patch:
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

def select_pengguna(conn, nama):
    cur = conn.cursor()
    query = """SELECT * FROM pengguna WHERE nama=?"""
    cur.execute(query, (nama,))
    rows = cur.fetchall()
    return rows

# Contoh penggunaan:
db_file = "database.db"
conn = create_connection(db_file)
if conn is not None:
    nama = "JohnDoe"
    rows = select_pengguna(conn, nama)
    for row in rows:
        print(row)
else:
    print("Error! tidak bisa membuat koneksi database.")
