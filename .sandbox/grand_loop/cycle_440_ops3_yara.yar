rule detect_sql_injection_ellipsis {
  strings:
    $sql = { 0x53 0x45 0x4c 0x45 0x43 0x54 } // SELECT
  condition:
    $sql at pe.data_offset
}