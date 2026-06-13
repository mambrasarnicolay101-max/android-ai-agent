rule detect_jwt_manual {
  meta:
    description = "Deteksi token JWT manual"
    author = "Blue Team"
  strings:
    $jwt_header = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
  condition:
    $jwt_header at 0
}

rule detect_invalid_input {
  meta:
    description = "Deteksi input invalid"
    author = "Blue Team"
  strings:
    $invalid_input = "text"
  condition:
    $invalid_input at 0
}