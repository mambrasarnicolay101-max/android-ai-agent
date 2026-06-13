rule detect_command_injection {
    meta:
        description = "Detect Command Injection"
        author = "Blue Team"
    strings:
        $cmd_injection = "cmd=" nocase
    condition:
        $cmd_injection
}

rule detect_broken_access_control {
    meta:
        description = "Detect Broken Access Control"
        author = "Blue Team"
    strings:
        $access_control = "token=" nocase
    condition:
        not $access_control
}

rule detect_security_misconfiguration {
    meta:
        description = "Detect Security Misconfiguration"
        author = "Blue Team"
    strings:
        $misconfiguration = "Server: " nocase
    condition:
        $misconfiguration
}