# Kode patch untuk mengatasi kerentanan yang ditemukan
# Contoh: Perbaikan kerentanan SQL Injection
import sqlite3

# Sebelumnya
# query = "SELECT * FROM usuarios WHERE username = '" + username + "' AND password = '" + password + "'"
# cursor.execute(query)

# Setelah patch
query = "SELECT * FROM usuarios WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
