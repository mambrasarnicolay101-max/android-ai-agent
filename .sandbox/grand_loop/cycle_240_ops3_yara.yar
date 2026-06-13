rule detect_malware_ellipsis {
  meta:
    author = "Blue Team"
    description = "Deteksi malware ellipsis"
  strings:
    $a = { 6a 00 00 00 00 00 }
    $b = { 6a 01 00 00 00 00 }
  condition:
    all of them
}