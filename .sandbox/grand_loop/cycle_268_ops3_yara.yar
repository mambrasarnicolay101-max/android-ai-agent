rule detect_injection {
    meta:
        author = "Tim Keamanan"
        description = "Aturan untuk mendeteksi injeksi SQL"
    strings:
        $sql_injection = "SELECT|INSERT|UPDATE|DELETE"
    condition:
        $sql_injection
}