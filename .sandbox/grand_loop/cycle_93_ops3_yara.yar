rule detect_serangan {
    meta:
        description = "Aturan untuk mendeteksi serangan"
        author = "Nama Anda"
    strings:
        $base64 = { 24 62 69 74 73 }
    condition:
        $base64 at 0
}