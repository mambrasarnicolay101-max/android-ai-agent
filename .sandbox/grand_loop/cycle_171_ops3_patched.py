# Contoh kode yang sudah diperbaiki
# Sebelumnya:
# def proses_input(user_input):
#     return eval(user_input)

# Setelah patch:
def proses_input(user_input):
    try:
        # Menggunakan ast.literal_eval yang lebih aman
        return ast.literal_eval(user_input)
    except ValueError:
        return "Input tidak valid"
    except Exception as e:
        return f"Terjadi kesalahan: {e}"
