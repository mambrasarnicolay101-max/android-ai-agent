rule detect_command_injection {
  strings:
    $s1 = "cmd=" nocase
    $s2 = ";|&||" nocase
  condition:
    $s1 and $s2
}