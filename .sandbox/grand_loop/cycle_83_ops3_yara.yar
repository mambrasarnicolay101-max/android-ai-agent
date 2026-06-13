rule detect_sql_injection
{
    meta:
        description = "Deteksi serangan SQL Injection"
        author = "Blue Team"
    strings:
        $sql_inject = { "OR 1=1" }
    condition:
        $sql_inject
}