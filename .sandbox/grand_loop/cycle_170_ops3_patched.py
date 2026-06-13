# Contoh patch untuk vulnerability yang ditemukan
def validate_input(data):
    # Validasi input untuk mencegah serangan injeksi
    if not isinstance(data, str):
        raise ValueError("Input harus berupa string")
    if len(data) > 1024:
        raise ValueError("Input terlalu panjang")

def handle_request(request):
    # Handling request dengan validasi input
    try:
        validate_input(request['data'])
        # Proses request
    except ValueError as e:
        # Tangani error
        print(f"Error: {e}")
