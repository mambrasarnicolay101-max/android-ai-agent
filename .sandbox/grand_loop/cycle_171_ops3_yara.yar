rule detect_injection_ellipsis {
    meta:
        description = "Mendeteksi serangan injeksi kode"
        author = "Blue Team"
    strings:
        $a = "eval(" ascii
        $b = "exec(" ascii
    condition:
        any of them
}