rule detect_Broken_Access_Control {
  meta:
    description = "Deteksi Broken Access Control"
    author = "Blue Team"
  strings:
    $auth = "Authorization: "
  condition:
    $auth at 0
}

rule detect_Cryptographic_Failures {
  meta:
    description = "Deteksi Cryptographic Failures"
    author = "Blue Team"
  strings:
    $jwt = "jwt."
    $secret = "secretkey"
  condition:
    $jwt at 0 and $secret at 0
}

rule detect_Injection {
  meta:
    description = "Deteksi Injection"
    author = "Blue Team"
  strings:
    $query = "query:"
    $or = "OR 1=1"
  condition:
    $query at 0 and $or at 0
}