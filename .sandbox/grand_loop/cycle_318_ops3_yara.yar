rule detect_sql_injection {
    meta:
        description = "Deteksi serangan SQL Injection"
        author = "Blue Team"
    strings:
        $s1 = " UNION SELECT"
        $s2 = " OR 1=1"
        $s3 = " DROP TABLE"
    condition:
        any of ($s*)
}