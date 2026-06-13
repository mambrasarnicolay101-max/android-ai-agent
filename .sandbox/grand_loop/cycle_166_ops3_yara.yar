rule detect_suspicious_activity {
  strings:
    $a = "suspicious_string"
  condition:
    $a
}