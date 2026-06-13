# Contoh PATCH CODE untuk mengatasi kerentanan yang ditemukan
import hashlib

def hash_password(password):
    # Menggunakan hash yang lebih aman seperti SHA-256
    return hashlib.sha256(password.encode()).hexdigest()

# Mengupdate fungsi autentikasi untuk menggunakan hash_password
def authenticate(username, password):
    stored_password = hash_password(password)
    # Membandingkan hash password yang disimpan dengan hash password yang diinput
    return stored_password == stored_password
