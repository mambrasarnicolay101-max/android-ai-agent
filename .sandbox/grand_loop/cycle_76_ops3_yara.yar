rule detect_broken_access_control {
    meta:
        description = "Deteksi akses tidak sah ke endpoint protected"
        author = "Tim Blue"
    strings:
        $url = "/protected"
    condition:
        $url at @http.request.uri
}

rule detect_cryptographic_failures {
    meta:
        description = "Deteksi penggunaan kunci rahasia yang tidak aman"
        author = "Tim Blue"
    strings:
        $secret_key = "super-secret"
    condition:
        $secret_key at @http.request.headers
}

rule detect_injection {
    meta:
        description = "Deteksi serangan SQL injection"
        author = "Tim Blue"
    strings:
        $ injection = "' OR 1=1 --"
    condition:
        $injection at @http.request.body
}