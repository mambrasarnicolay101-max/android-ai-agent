rule detect_sql_injection {
  meta:
    description = "Aturan untuk mendeteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $a = "SELECT * FROM"
    $b = "WHERE username ="
    $c = "AND password ="
  condition:
    $a and $b and $c
}