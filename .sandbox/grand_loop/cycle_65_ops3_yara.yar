rule detect_sql_injection {
  strings:
    $s1 = "SELECT * FROM users WHERE username=" nocase
    $s2 = "AND password=" nocase
  condition:
    all of them
}