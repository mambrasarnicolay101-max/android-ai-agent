rule detect_serbuan {
    meta:
        description = "Aturan untuk mendeteksi serbuan"
        author = "Namamu"
    strings:
        $a = "string_khusus_yang_dicari"
    condition:
        $a
}