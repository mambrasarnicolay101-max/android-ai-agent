rule detect_sql_injection {
  strings:
    $sql_keyword = "SELECT" nocase
    $sql_keyword2 = "FROM" nocase
    $sql_keyword3 = "WHERE" nocase
  condition:
    all of them
}