rule detect_serbuan {
    meta:
        description = "Aturan untuk mendeteksi serangan serbuan"
    strings:
        $a = "serbuan"
    condition:
        $a
}