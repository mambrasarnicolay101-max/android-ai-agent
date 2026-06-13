# Import library yang dibutuhkan
import hashlib

# Fungsi untuk melakukan patch pada kerentanan yang ditemukan
def patch_kerentanan(data):
    # Enkripsi data menggunakan hashlib
    encrypted_data = hashlib.sha256(data.encode()).hexdigest()
    return encrypted_data

# Contoh penggunaan fungsi patch_kerentanan
data_asli = "contoh_data"
data_PATCHED = patch_kerentanan(data_asli)
print("Data asli:", data_asli)
print("Data patched:", data_PATCHED)
