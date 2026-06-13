# Kode patch untuk memperbaiki kerentanan
def validate_input(data):
    if not isinstance(data, str):
        raise ValueError("Input harus berupa string")
    if len(data) > 100:
        raise ValueError("Input terlalu panjang")

def patch_vulnerability(data):
    try:
        validate_input(data)
        # Kode yang aman untuk mengolah input
        return data.strip()
    except ValueError as e:
        # Handle kesalahan input
        return str(e)

# Contoh penggunaan
data = "Contoh input"
print(patch_vulnerability(data))
