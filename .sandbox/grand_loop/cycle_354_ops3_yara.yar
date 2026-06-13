rule detect_suspect_activity {
    meta:
        description = "Aturan untuk mendeteksi kegiatan mencurigakan"
        author = "Blue Team"
    strings:
        $a = { 6f 77 6e 65 72 20 }
    condition:
        $a at 0
}