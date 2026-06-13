rule detect_exploit {
  meta:
    description = "Deteksi eksploitasi serupa"
    author = "Blue Team"
  strings:
    $a = {6a 00 00 00 00 00} // bytes yang mencurigakan
  condition:
    $a at entry0
}