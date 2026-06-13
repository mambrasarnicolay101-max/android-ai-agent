# Contoh kode yang sudah diperbaiki
def validate_input(data):
    if not isinstance(data, str):
        raise ValueError("Input harus berupa string")
    data = data.strip()
    if not data:
        raise ValueError("Input tidak boleh kosong")
    return data

def proses_data(data):
    try:
        data = validate_input(data)
        # Proses data yang sudah divalidasi
        return True
    except ValueError as e:
        print(f"Error: {e}")
        return False
