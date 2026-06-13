rule detect_sql_injection {
    meta:
        description = "Aturan untuk mendeteksi injeksi SQL"
        author = "Blue Team"
    strings:
        $s1 = "UNION SELECT"
        $s2 = "OR 1=1"
    condition:
        any of ($s1, $s2)
}