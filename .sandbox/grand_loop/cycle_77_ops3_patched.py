# Contoh kode yang sudah diperbaiki
def validate_input(data):
    if not isinstance(data, str):
        raise ValueError("Input harus berupa string")
    if len(data) > 100:
        raise ValueError("Input terlalu panjang")
    return data

def handle_request(request):
    try:
        data = validate_input(request.get("data"))
        # Proses data yang telah divalidasi
        return {"status": "sukses"}
    except ValueError as e:
        return {"status": "gagal", "error": str(e)}
