rule detect_sql_injection {
  strings:
    $sql = "SELECT * FROM users"
  condition:
    $sql
}