# Contoh kode yang sudah diperbaiki
# Misalnya, jika kerentanan yang ditemukan adalah kesalahan validasi input
def validate_input(data):
    if not isinstance(data, str):
        return False
    if len(data) > 100:
        return False
    return True

# Sebelumnya
def proses_data(data):
    # Tidak ada validasi
    hasil = proses(data)
    return hasil

# Setelah patch
def proses_data(data):
    if validate_input(data):
        hasil = proses(data)
        return hasil
    else:
        return "Input tidak valid"
