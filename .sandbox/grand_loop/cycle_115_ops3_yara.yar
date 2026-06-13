rule detect_sql_injection {
    meta:
        author = "Blue Team"
        description = "Deteksi serangan SQL Injection"
    strings:
        $sql_injection = /SELECT\s+.*\s+FROM/
        $sql_injection2 = /INSERT\s+.*\s+INTO/
        $sql_injection3 = /UPDATE\s+.*\s+SET/
        $sql_injection4 = /DELETE\s+.*\s+FROM/
    condition:
        1 of them
}

rule detect_cross_site_scripting {
    meta:
        author = "Blue Team"
        description = "Deteksi serangan Cross-Site Scripting (XSS)"
    strings:
        $xss = /<script>/
        $xss2 = /</script>/
    condition:
        1 of them
}