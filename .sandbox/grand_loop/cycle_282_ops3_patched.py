# Contoh kode patch untuk memperbaiki kerentanan SQL Injection
import sqlite3

# Sebelumnya
# cursor.execute("SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'")

# Setelah patch
cursor = sqlite3.connect("database.db").cursor()
query = "SELECT * FROM users WHERE username=? AND password=?"
cursor.execute(query, (username, password))
