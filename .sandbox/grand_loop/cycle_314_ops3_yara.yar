rule detect_sql_injection {
  meta:
    description = "Deteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $a = "UNION SELECT"
    $b = "OR 1=1"
  condition:
    any of them
}