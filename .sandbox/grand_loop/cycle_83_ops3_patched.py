# Kode patch untuk mengatasi kerentanan
# Contoh: Memperbaiki kerentanan SQL Injection
import mysql.connector

# Sebelumnya
# cursor.execute("SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'")

# Sesudah patch
cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
