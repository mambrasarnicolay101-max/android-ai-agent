rule detect_sql_injection {
  meta:
    description = "Detect SQL Injection"
    author = "Blue Team"
  strings:
    $s1 = "SELECT * FROM"
    $s2 = "UNION"
    $s3 = "OR 1=1"
  condition:
    any of them
}

rule detect_xss {
  meta:
    description = "Detect Cross-Site Scripting (XSS)"
    author = "Blue Team"
  strings:
    $s1 = "<script>"
    $s2 = "javascript:"
    $s3 = "alert("
  condition:
    any of them
}