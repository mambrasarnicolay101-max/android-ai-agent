rule detect_sql_injection {
    meta:
        description = "Deteksi SQL Injection"
        author = "CSO"
    strings:
        $sqlInject1 = "SELECT * FROM"
        $sqlInject2 = "INSERT INTO"
        $sqlInject3 = "UPDATE "
        $sqlInject4 = "DELETE FROM"
    condition:
        any of ($sqlInject*)
}