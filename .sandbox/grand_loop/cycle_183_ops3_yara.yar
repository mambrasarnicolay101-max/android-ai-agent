rule detect_malicious_activity {
    meta:
        description = "Aturan untuk mendeteksi aktivitas malicious"
        author = "Blue Team"
    strings:
        $a = "string malicious"
    condition:
        $a
}