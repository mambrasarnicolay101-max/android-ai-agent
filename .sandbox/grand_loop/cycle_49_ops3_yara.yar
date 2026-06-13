rule detect_sql_injection {
  meta:
    description = "Deteksi serangan SQL Injection"
  strings:
    $sql_inject = {SELECT|INSERT|UPDATE|DELETE}
  condition:
    $sql_inject
}