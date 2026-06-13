rule detect_malware_ellipse {
    meta:
        description = "Detect Ellipse Malware"
        author = "Blue Team"
    strings:
        $a = " ellipse"
    condition:
        $a
}