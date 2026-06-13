rule detect_sql_injection {
  meta:
    author = "Blue Team"
    description = "Deteksi serangan SQL Injection"
  strings:
    $s1 = "SELECT * FROM users WHERE username = '"
    $s2 = "AND password = '"
  condition:
    any of them
}