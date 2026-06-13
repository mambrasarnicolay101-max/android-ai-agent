rule detect_sql_injection {
    meta:
        description = "Deteksi serangan SQL Injection"
        author = "Blue Team"
    strings:
        $sql_query = "SELECT * FROM"
        $sql_query2 = "INSERT INTO"
        $sql_query3 = "UPDATE"
        $sql_query4 = "DELETE FROM"
    condition:
        any of ($sql_query*, $sql_query2*, $sql_query3*, $sql_query4*)
}

rule detect_xss {
    meta:
        description = "Deteksi serangan Cross-Site Scripting (XSS)"
        author = "Blue Team"
    strings:
        $script_tag = "<script>"
        $script_tag2 = "</script>"
    condition:
        any of ($script_tag, $script_tag2)
}