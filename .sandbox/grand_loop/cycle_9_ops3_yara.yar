rule detect_broken_access_control {
  meta:
    description = "Detect broken access control"
    author = "Blue Team"
  strings:
    $auth = "Authorization: Bearer"
  condition:
    $auth
}

rule detect_cryptographic_failures {
  meta:
    description = "Detect cryptographic failures"
    author = "Blue Team"
  strings:
    $secret_key = "secretkey"
  condition:
    $secret_key
}

rule detect_injection {
  meta:
    description = "Detect injection attacks"
    author = "Blue Team"
  strings:
    $xss = "<script>"
  condition:
    $xss
}

rule detect_insecure_design {
  meta:
    description = "Detect insecure design"
    author = "Blue Team"
  strings:
    $login = "login"
    $password = "password"
  condition:
    $login and $password
}