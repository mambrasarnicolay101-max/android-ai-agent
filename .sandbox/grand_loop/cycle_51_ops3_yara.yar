rule detect_SQLInjection_Ellipsis {
    meta:
        description = "Deteksi SQL Injection"
        author = "Blue Team"
    strings:
        $sql_inject = { or 1=1 -- }
    condition:
        $sql_inject
}