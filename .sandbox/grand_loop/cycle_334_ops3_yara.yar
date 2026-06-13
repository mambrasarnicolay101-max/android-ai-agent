rule detect_sql_injection {
  meta:
    description = "Deteksi SQL Injection"
    author = "Tim Keamanan"
  strings:
    $sql = "SELECT|INSERT|UPDATE|DELETE"
    $inj = "OR 1=1|UNION SELECT|WHERE 1=1"
  condition:
    $sql and $inj
}