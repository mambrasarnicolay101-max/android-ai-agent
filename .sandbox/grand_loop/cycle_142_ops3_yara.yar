rule detect_potential_xss {
    meta:
        description = "Aturan untuk mendeteksi potensi serangan XSS"
        author = "Tim Blue"
    strings:
        $script_tag = "<script>"
        $html_tag = "<html>"
    condition:
        $script_tag or $html_tag
}