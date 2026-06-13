rule detect_injection {
    meta:
        author = "Blue Team"
        description = "Deteksi injeksi kode"
    strings:
        $s1 = "SELECT * FROM"
        $s2 = "INSERT INTO"
        $s3 = "UPDATE"
        $s4 = "DELETE FROM"
    condition:
        any of ($s*)
}