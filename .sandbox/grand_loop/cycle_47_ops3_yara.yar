rule detect_sql_injection {
  meta:
    description = "Deteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $sql_query = { "SELECT" "FROM" "WHERE" }
    $sql_injection = { "'" "OR" "1=1" }
  condition:
    $sql_query and $sql_injection
}