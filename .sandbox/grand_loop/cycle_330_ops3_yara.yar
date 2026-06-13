rule detect_sql_injection {
    meta:
        description = "Deteksi serangan SQL Injection"
        author = "Blue Team"
    strings:
        $sql_inject = {SELECT|INSERT|UPDATE|DELETE}
    condition:
        $sql_inject
}