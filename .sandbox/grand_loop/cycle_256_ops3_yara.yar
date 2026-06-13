rule detect_serangan {
    meta:
        author = "Blue Team"
        description = "Mendeteksi serangan dengan pola tertentu"
    strings:
        $pattern1 = "pola_serangan_1"
        $pattern2 = "pola_serangan_2"
    condition:
        any of ($pattern*)
}