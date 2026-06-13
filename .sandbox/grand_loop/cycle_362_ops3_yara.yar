rule detect_sql_injection_ellipsis {
    meta:
        description = "Deteksi serangan SQL Injection"
        author = "Blue Team"
    strings:
        $a = "SELECT * FROM users WHERE username = '"
        $b = "OR 1=1"
    condition:
        $a and $b
}