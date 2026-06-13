rule detect_vulnerability {
  meta:
    description = "Aturan untuk mendeteksi serangan"
    author = "Tim Blue"
  strings:
    $str1 = "string yang dicari"
  condition:
    $str1
}