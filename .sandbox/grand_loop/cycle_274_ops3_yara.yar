rule detect_sql_injection {
    meta:
        description = "Deteksi serangan SQL injection"
        author = "Blue Team"
    strings:
        $s1 = "SELECT" ascii
        $s2 = "INSERT" ascii
        $s3 = "UPDATE" ascii
        $s4 = "DELETE" ascii
    condition:
        any of them
}