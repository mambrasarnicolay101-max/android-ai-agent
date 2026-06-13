rule detect_broken_access_control {
    strings:
        $sql_query = "SELECT * FROM users WHERE username = ?"
    condition:
        $sql_query
}

rule detect_cryptographic_failures {
    strings:
        $hash_function = "md5"
    condition:
        $hash_function
}

rule detect_injection {
    strings:
        $sql_query = "INSERT INTO users (username, password) VALUES (?, ?)"
    condition:
        $sql_query
}

rule detect_insecure_design {
    strings:
        $login_function = "login"
    condition:
        $login_function
}