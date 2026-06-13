rule detect_SQL_Injection {
  meta:
    description = "Deteksi SQL Injection"
    author = "Blue Team"
  strings:
    $s1 = "SELECT * FROM"
    $s2 = "WHERE username ="
    $s3 = "AND password ="
  condition:
    all of them
}