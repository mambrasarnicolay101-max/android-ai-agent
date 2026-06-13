rule detect_malware_ellipsis {
    meta:
        description = "Aturan untuk mendeteksi malware"
        author = "Blue Team"
    strings:
        $a = "kode_malware"
    condition:
        $a
}