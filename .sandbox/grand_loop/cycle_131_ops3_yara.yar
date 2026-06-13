rule detect_sql_injection {
  meta:
    description = "Aturan untuk mendeteksi injeksi SQL"
    author = "Blue Team"
  strings:
    $s1 = "SELECT" nocase
    $s2 = "INSERT" nocase
    $s3 = "UPDATE" nocase
    $s4 = "DELETE" nocase
    $s5 = "OR 1=1" nocase
    $s6 = "UNION" nocase
  condition:
    any of them
}