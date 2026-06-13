# Contoh kode patch untuk memperbaiki kerentanan SQL Injection
import mysql.connector

# Sebelumnya
# query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
# cursor.execute(query)

# Setelah patch
query = "SELECT * FROM users WHERE username = %s AND password = %s"
cursor.execute(query, (username, password))
