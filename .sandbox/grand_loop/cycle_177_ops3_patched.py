import http.server
import socketserver
import urllib.parse
import subprocess
import os

PORT = int(os.environ.get("PORT", 5000))

class SecureHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        # Perbaikan 1: Validasi input dan autentikasi pengguna
        if "cmd" in query:
            cmd = query["cmd"][0]
            # Validasi input untuk mencegah command injection
            if not self.validate_input(cmd):
                self.send_response(403)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Access denied")
                return
            
            # Autentikasi pengguna
            if not self.authenticate_user():
                self.send_response(401)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Unauthorized")
                return

            try:
                # Menjalankan command dengan sanitasi
                output = subprocess.check_output(cmd, shell=False, text=True, stderr=subprocess.STDOUT)
                response = f"<html><body><h1>Command Output:</h1><pre>{output}</pre></body></html>"
            except subprocess.CalledProcessError as e:
                response = f"<html><body><h1>Error:</h1><pre>{e.output}</pre></body></html>"
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response.encode())

    def validate_input(self, input_str):
        # Validasi input untuk mencegah command injection
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")
        if not set(input_str).issubset(allowed_chars):
            return False
        return True

    def authenticate_user(self):
        # Autentikasi pengguna
        # Contoh: menggunakan token autentikasi
        token = self.headers.get("Authorization")
        if token != "secret_token":
            return False
        return True

httpd = socketserver.TCPServer(("", PORT), SecureHandler)
httpd.serve_forever()
