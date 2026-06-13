rule detect_malicious_ellipsis {
    meta:
        author = " BLUE TEAM"
        description = "Mendeteksi eksploitasi serangan ellipsis"
    strings:
        $a = "ellipsis" ascii
    condition:
        $a
}