rule detect_malware_eksploitasi {
  meta:
    description = "Deteksi eksploitasi serupa"
    author = "Blue Team"
  strings:
    $a = { 6a 00 00 00 6a 00 00 00 }
  condition:
    all of them
}