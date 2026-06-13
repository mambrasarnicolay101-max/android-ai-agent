rule detect_brute_force {
    meta:
        description = "Aturan untuk mendeteksi serangan brute force pada login"
        author = "Blue Team"
    strings:
        $a = "login.php"
        $b = "username=" ascii
        $c = "password=" ascii
    condition:
        all of them
}