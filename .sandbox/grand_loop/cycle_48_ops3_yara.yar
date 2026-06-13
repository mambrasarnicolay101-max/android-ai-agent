rule detect_suspect_code {
    meta:
        description = "Aturan untuk mendeteksi kode mencurigakan"
        author = "Blue Team"
    strings:
        $a = { 6C 6F 61 64 4C 49 42 72 61 72 79 }
    condition:
        $a at entrypoint
}