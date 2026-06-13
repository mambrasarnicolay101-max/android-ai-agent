rule detect_broken_access_control {
  meta:
    description = "Deteksi broken access control"
  strings:
    $a = { 70 6f 75 6e 64 20 61 63 63 65 73 73 20 63 6f 6e 74 72 6f 6c }
  condition:
    $a at 0
}

rule detect_sql_injection {
  meta:
    description = "Deteksi SQL injection"
  strings:
    $a = { 27 20 4f 52 20 31 3d 31 20 2d 2d }
  condition:
    $a at 0
}

rule detect_insecure_design {
  meta:
    description = "Deteksi insecure design"
  strings:
    $a = { 67 65 74 20 2f 63 61 72 6f 75 73 65 6c 73 }
  condition:
    $a at 0
}