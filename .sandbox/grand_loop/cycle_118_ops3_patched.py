# Kode sistem asli tidak disediakan, oleh karena itu contoh patch code ini bersifat umum
import hashlib

def validate_input(data):
    # Validasi input untuk mencegah serangan injeksi
    if not isinstance(data, str):
        return False
    return True

def hash_password(password):
    # Menggunakan hash yang lebih aman seperti bcrypt atauargon2
    salt = "salt_random"
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return hashed_password.hex()

# Contoh penggunaan
if __name__ == "__main__":
    password = "passwordku"
    if validate_input(password):
        hashed_password = hash_password(password)
        print(f"Password Hash: {hashed_password}")
    else:
        print("Input tidak valid")
