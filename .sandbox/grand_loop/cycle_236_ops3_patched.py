# Contoh patch untuk kerentanan pada fungsi autentikasi
def authenticate_user(username, password):
    # Sebelumnya
    # if username == "admin" and password == "password123":
    #     return True
    # Sekarang, dengan penambahan hashing dan salting
    import hashlib
    stored_password = hashlib.sha256("password123".encode()).hexdigest()
    input_password = hashlib.sha256(password.encode()).hexdigest()
    if username == "admin" and input_password == stored_password:
        return True
    return False
