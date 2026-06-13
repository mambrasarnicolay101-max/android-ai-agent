rule detect_sql_injection {
    meta:
        description = "Deteksi SQL Injection"
        author = "Blue Team"
    strings:
        $s1 = "SELECT * FROM"
        $s2 = "WHERE nama="
    condition:
        all of them
}