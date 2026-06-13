# Kode sistem asli tidak disediakan, namun berikut adalah contoh patch kode untuk kerentanan umum
# Misalnya, kerentanan SQL Injection
def get_user_data(username, password):
    # Sebelum patch
    # query = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password)
    # Patch: menggunakan parameter query untuk mencegah SQL Injection
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    return cursor.fetchall()

# Patch untuk kerentanan Cross-Site Scripting (XSS)
def render_template(template_name, **kwargs):
    # Sebelum patch
    # return render_template(template_name, **kwargs)
    # Patch: menggunakan escape HTML untuk mencegah XSS
    from markupsafe import escape
    kwargs = {key: escape(value) for key, value in kwargs.items()}
    return render_template(template_name, **kwargs)
