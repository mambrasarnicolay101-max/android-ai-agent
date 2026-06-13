rule detect_serangan_ellipsis
{
    meta:
        description = "Aturan untuk mendeteksi serangan ellipsis"
        author = "Blue Team"
    strings:
        $a = "Ellipsis" ascii
    condition:
        $a
}