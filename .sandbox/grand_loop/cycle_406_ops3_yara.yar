rule detect_sql_injection {
  meta:
    description = "Aturan untuk mendeteksi eksploitasi SQL Injection"
    author = "Blue Team"
  strings:
    $s1 = "SELECT * FROM users WHERE"
    $s2 = "OR 1=1"
    $s3 = "UNION SELECT"
  condition:
    $s1 and ($s2 or $s3)
}