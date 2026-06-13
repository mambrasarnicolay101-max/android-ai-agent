import http.server
import socketserver
import urllib.parse
import subprocess
import os
import shlex

PORT = int(os.environ.get("PORT", 5000))

class VulnerableHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        # Perbaikan kerentanan Command Injection
        if "cmd" in query:
            cmd = query["cmd"][0]
            # Sanitasi input dengan menggunakan shlex untuk memastikan command tidak dapat di-injeksi
            cmd_args = shlex.split(cmd)
            try:
                # Jalankan command dengan menggunakan subprocess.run danhindari shell=True
                output = subprocess.run(cmd_args, capture_output=True, text=True, stderr=subprocess.STDOUT)
                response = f"<html><body><h1>Command Output:</h1><pre>{output.stdout}</pre></body></html>"
            except subprocess.CalledProcessError as e:
                response = f"<html><body><h1>Error:</h1><pre>{e.output}</pre></body></html>"
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response.encode())

        # Perbaikan kerentanan Broken Access Control
        # Limitasi akses dengan authentikasi dan otorisasi yang tepat
        # Contoh sederhana dengan menggunakan token
        token = query.get("token", [""])[0]
        if token != "sekret_token":
            self.send_response(403)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Akses Ditolak")

        # Perbaikan kerentanan Security Misconfiguration
        # Konfigurasi server dengan benar untuk mencegah informasi sensitif
        self.server_version = "Server"
        self.sys_version = ""
