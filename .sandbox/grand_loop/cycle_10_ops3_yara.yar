rule detect_broken_access_control {
  meta:
    description = "Detect broken access control"
    author = "Blue Team"
  strings:
    $url = "/carousel"
  condition:
    $url at @entry(0)
}