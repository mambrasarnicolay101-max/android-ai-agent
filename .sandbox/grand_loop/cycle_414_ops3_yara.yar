rule detect_serangan {
  meta:
    description = "Aturan untuk mendeteksi serangan"
    author = "Blue Team"
  strings:
    $a = { 6c 6f 61 64 28 29 }
    $b = { 73 79 73 74 65 6d 28 29 }
  condition:
    any of ($a, $b)
}