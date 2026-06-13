# Contoh kode patch untuk kerentanan SQL Injection
def login(username, password):
    # Menggunakan parameterized query untuk mencegah SQL Injection
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    return cursor.fetchone()
