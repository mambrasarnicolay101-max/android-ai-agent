# Contoh kode yang sudah diperbaiki
# Misalnya, kita asumsikan ada kerentanan pada fungsi login
def login(username, password):
    # Sebelumnya, mungkin ada kerentanan seperti ini
    # query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    
    # Sekarang, kita menggunakan parameterized query untuk mencegah SQL Injection
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    
    # Kita juga menambahkan validasi input untuk mencegah Cross-Site Scripting (XSS)
    if not validate_input(username) or not validate_input(password):
        return "Input tidak valid"
    
    # Kita juga menambahkan autentikasi dua faktor untuk meningkatkan keamanan
    if not authenticatie_dua_faktor(username, password):
        return "Autentikasi gagal"
    
    return "Login sukses"
