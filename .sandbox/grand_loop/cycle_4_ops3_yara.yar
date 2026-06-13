rule detect_broken_access_control
{
  meta:
    description = "Deteksi akses tidak sah ke endpoint /carousel"
    author = "Blue Team"
  strings:
    $curl = "curl -X POST -H \"Content-Type: application/json\" -d"
  condition:
    $curl at @entry
}

rule detect_cryptographic_failures
{
  meta:
    description = "Deteksi pembuatan token JWT yang tidak sah"
    author = "Blue Team"
  strings:
    $jwt = "jwt.encode"
  condition:
    $jwt at @entry
}

rule detect_injection
{
  meta:
    description = "Deteksi MongoDB injection"
    author = "Blue Team"
  strings:
    $mongodb = "mongodb://localhost/social-media-carousel"
  condition:
    $mongodb at @entry
}