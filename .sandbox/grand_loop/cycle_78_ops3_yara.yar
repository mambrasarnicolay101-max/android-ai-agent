rule detect_broken_access_control {
  meta:
    description = "Deteksi akses tidak sah ke desain PCB"
    author = "Blue Team"
  strings:
    $url = "/designs/<int:design_id>"
  condition:
    $url at offset 0
}

rule detect_sql_injection {
  meta:
    description = "Deteksi serangan SQL Injection"
    author = "Blue Team"
  strings:
    $payload = "OR 1=1"
  condition:
    $payload at offset 0
}