rule detect_sql_injection {
  meta:
    description = "Deteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $s1 = "SELECT * FROM"
    $s2 = "WHERE"
    $s3 = "INSERT INTO"
  condition:
    any of ($s*)
}