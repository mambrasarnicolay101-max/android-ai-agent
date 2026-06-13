rule detect_sql_injection {
  meta:
    description = "Deteksi SQL Injection"
    author = "Blue Team"
  strings:
    $sql_inject = "SELECT * FROM users WHERE"
  condition:
    $sql_inject
}