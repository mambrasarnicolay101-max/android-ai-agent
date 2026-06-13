import http.server
import socketserver
import urllib.parse
import subprocess
import os

PORT = int(os.environ.get("PORT", 5000))

class VulnerableHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        # Vulnerability 1: Command Injection
        if "cmd" in query:
            cmd = query["cmd"][0]
            try:
                # VULNERABLE: Menjalankan command secara langsung tanpa sanitasi
                output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
                response = f"<html><body><h1>Command Output:</h1><pre>{output}</pre></body></html>"
            except subprocess.CalledProcessError as e:
                response = f"<html><body><h1>Error:</h1><pre>{e.output}</pre></body></html>"
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))
            return

        # Default Response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = """
        <html>
            <head><title>Damn Vulnerable Native App</title></head>
            <body>
                <h1>Welcome to DVNA (Damn Vulnerable Native App)</h1>
                <p>A lightweight third-party target simulation.</p>
                <ul>
                    <li><a href="/?cmd=echo%20hello">Test Echo</a></li>
                    <li><a href="/?cmd=dir">Test Dir</a></li>
                </ul>
            </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), VulnerableHandler) as httpd:
        print(f"Serving Damn Vulnerable Native App at port {PORT}")
        httpd.serve_forever()
