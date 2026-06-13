# Kode yang sudah diperbaiki
# Asumsi bahwa kode sistem asli memiliki kerentanan pada fungsi auth()
def auth(username, password):
    # Perbaikan: Validasi input dan penggunaan hashing yang aman
    if not isinstance(username, str) or not isinstance(password, str):
        return False
    # Penggunaan hashing yang aman seperti bcrypt
    import bcrypt
    stored_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return bcrypt.checkpw(password.encode('utf-8'), stored_password)
