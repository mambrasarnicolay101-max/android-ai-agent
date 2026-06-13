rule detect_sql_injection {
  meta:
    description = "Aturan untuk mendeteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $sql_inject = "UNION SELECT"
    $sql_inject2 = "OR 1=1"
  condition:
    any of ($sql_inject*) or any of ($sql_inject2*)
}