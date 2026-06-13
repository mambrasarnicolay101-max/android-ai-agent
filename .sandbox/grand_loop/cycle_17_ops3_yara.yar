rule detect_suspicious_activity {
    meta:
        author = "Blue Team"
        description = "Mendeteksi aktivitas mencurigakan"
    strings:
        $s1 = "string_suspicious_1"
        $s2 = "string_suspicious_2"
    condition:
        $s1 or $s2
}