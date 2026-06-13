rule detect_sql_injection {
  meta:
    description = "Deteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $s1 = "SELECT * FROM"
    $s2 = "UNION SELECT"
    $s3 = "OR 1=1"
  condition:
    any of ($s*)
}