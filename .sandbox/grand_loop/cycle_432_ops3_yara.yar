rule detect_login_attempt {
    meta:
        author = "Blue Team"
        description = "Deteksi login attempt"
    strings:
        $a = "username="
        $b = "password="
    condition:
        all of them
}

rule detect_file_upload {
    meta:
        author = "Blue Team"
        description = "Deteksi file upload"
    strings:
        $a = "Content-Type: image/jpeg"
        $b = "Content-Type: image/png"
    condition:
        all of them
}