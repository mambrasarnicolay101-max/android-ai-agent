rule detect_sql_injection {
  meta:
    description = "Aturan untuk mendeteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $s1 = "OR 1=1"
    $s2 = "UNION ALL SELECT"
  condition:
    any of them
}