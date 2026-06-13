rule detect_jwt_injection {
    meta:
        description = "JWT injection"
        author = "Your Name"
    strings:
        $a = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    condition:
        $a at 0
}

rule detect_xss {
    meta:
        description = "XSS"
        author = "Your Name"
    strings:
        $a = "<script>"
    condition:
        $a at 0
}

rule detect_ssrfr {
    meta:
        description = "SSRF"
        author = "Your Name"
    strings:
        $a = "http://localhost:27017/"
    condition:
        $a at 0
}