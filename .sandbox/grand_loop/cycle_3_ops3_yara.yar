rule detect_broken_access_control {
  meta:
    description = "Deteksi akses tidak sah ke endpoint /template"
    author = "Blue Team"
  strings:
    $str1 = "/template"
  condition:
    $str1
}

rule detect_cryptographic_failures {
  meta:
    description = "Deteksi pembobolan token JWT"
    author = "Blue Team"
  strings:
    $str1 = "jwt.sign"
    $str2 = "secretkey"
  condition:
    $str1 and $str2
}

rule detect_insecure_design {
  meta:
    description = "Deteksi pembuatan template dengan nama yang sama"
    author = "Blue Team"
  strings:
    $str1 = "/template"
    $str2 = "name="
  condition:
    $str1 and $str2
}

rule detect_security_misconfiguration {
  meta:
    description = "Deteksi akses ke aplikasi melalui URL yang tidak aman"
    author = "Blue Team"
  strings:
    $str1 = "http://"
  condition:
    $str1
}