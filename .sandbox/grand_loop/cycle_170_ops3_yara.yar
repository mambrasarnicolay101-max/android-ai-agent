rule detect_malware_ellip {
    meta:
        description = "Deteksi malware elliptic curve"
        author = "Blue Team"
    strings:
        $a = { 6a 00 00 00 01 00 00 00 }
        $b = { 6a 00 00 00 02 00 00 00 }
    condition:
        $a and $b
}