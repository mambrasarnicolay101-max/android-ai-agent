rule detect_sql_injection {
    meta:
        description = "Deteksi serangan SQL Injection"
        author = "Tim Keamanan"
    strings:
        $sql_keyword = "SELECT|INSERT|UPDATE|DELETE"
    condition:
        $sql_keyword
}