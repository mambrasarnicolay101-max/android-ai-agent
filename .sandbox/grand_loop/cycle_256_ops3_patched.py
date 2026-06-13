# Contoh kode patch untuk memperbaiki kerentanan
def validate_input(data):
    if not isinstance(data, str):
        raise ValueError("Input harus berupa string")
    if len(data) > 100:
        raise ValueError("Input terlalu panjang")
    return data.strip()

def process_data(data):
    validated_data = validate_input(data)
    # Proses data yang telah divalidasi
    return validated_data
