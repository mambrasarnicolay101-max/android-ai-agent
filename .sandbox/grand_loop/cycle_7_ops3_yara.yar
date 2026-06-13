rule detect_insecure_login {
  meta:
    description = "Insecure login attempt"
    author = "Blue Team"
  strings:
    $a = "username=admin&password=password"
  condition:
    $a
}

rule detect_jwt_token_manipulation {
  meta:
    description = "JWT token manipulation attempt"
    author = "Blue Team"
  strings:
    $a = "jwt.sign"
    $b = "jwt.verify"
  condition:
    $a or $b
}

rule detect_xss_attempt {
  meta:
    description = "XSS attempt"
    author = "Blue Team"
  strings:
    $a = "<script>"
  condition:
    $a
}