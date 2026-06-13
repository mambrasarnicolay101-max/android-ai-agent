# Contoh kode patch untuk memperbaiki kerentanan pada fungsi login
def login(username, password):
    # Validasi input
    if not isinstance(username, str) or not isinstance(password, str):
        return "Input harus berupa string"
    
    # Hash password untuk membandingkan dengan password yang tersimpan
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Query database untuk membandingkan username dan password
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, hashed_password))
    
    # Jika data ditemukan, maka login berhasil
    if cursor.fetchone():
        return "Login berhasil"
    else:
        return "Login gagal"

# Contoh kode patch untuk memperbaiki kerentanan pada fungsi upload file
def upload_file(file):
    # Validasi jenis file
    if file.type != "image/jpeg" and file.type != "image/png":
        return "Jenis file tidak diizinkan"
    
    # Simpan file ke direktori yang aman
    file.save("/path/to/secure/directory/")
    
    return "File uploaded berhasil"
