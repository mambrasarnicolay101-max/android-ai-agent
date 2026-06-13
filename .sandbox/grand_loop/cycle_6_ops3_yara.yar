rule detect_BrokenAccessControl {
    meta:
        description = "Broken Access Control"
    strings:
        $a1 = "/social-card"
        $a2 = "POST"
    condition:
        all of ($a*)
}

rule detect_CryptographicFailures {
    meta:
        description = "Cryptographic Failures"
    strings:
        $b1 = "password"
        $b2 = "plaintext"
    condition:
        all of ($b*)
}

rule detect_Injection {
    meta:
        description = "SQL Injection"
    strings:
        $c1 = "SQL"
        $c2 = "query"
    condition:
        all of ($c*)
}