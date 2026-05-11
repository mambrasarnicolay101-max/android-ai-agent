def handle_user_input(user_id):
    # DUMMY VULNERABILITY: SQL Injection
    query = "SELECT * FROM users WHERE id = " + user_id
    return query

def execute_command(cmd):
    # DUMMY VULNERABILITY: Command Injection
    import os
    import subprocess
    subprocess.run(["echo", cmd])  # PATCHED: Command Injection mitigated
