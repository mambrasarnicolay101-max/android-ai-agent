rule detect_broken_access_control {
  meta:
    description = "Deteksi Broken Access Control"
  strings:
    $a = "http://localhost:5000/login"
  condition:
    $a
}

rule detect_cryptographic_failures {
  meta:
    description = "Deteksi Cryptographic Failures"
  strings:
    $a = "super-secret"
  condition:
    $a
}

rule detect_injection {
  meta:
    description = "Deteksi Injection"
  strings:
    $a = "/register"
    $b = "{ '$ne': '' }"
  condition:
    $a and $b
}