rule detect_sql_injection {
  meta:
    description = "Deteksi SQL Injection"
    author = "Blue Team"
  strings:
    $a = "OR 1=1"
    $b = "UNION SELECT"
  condition:
    $a or $b
}