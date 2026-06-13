# Contoh kode yang sudah diperbaiki
import os

def validate_input(input_data):
    if not isinstance(input_data, str):
        raise ValueError("Input harus berupa string")
    if len(input_data) > 100:
        raise ValueError("Input terlalu panjang")
    return input_data

def proses_data(data):
    try:
        # Validasi input
        valid_data = validate_input(data)
        # Proses data yang sudah divalidasi
        return valid_data.upper()
    except ValueError as e:
        # Tangani kesalahan input
        return str(e)

# Contoh penggunaan
input_data = "contoh input"
output = proses_data(input_data)
print(output)
