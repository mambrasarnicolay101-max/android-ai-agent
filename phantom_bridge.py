import subprocess
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# KONFIGURASI PHANTOM
ADB_PATH = r"C:\Users\ASUS\AppData\Local\Android\Sdk\platform-tools\adb.exe"
PORT = 8081  # Port untuk stream visual

class PhantomStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--boundary')
            self.end_headers()
            try:
                while True:
                    # Ambil snapshot mentah via ADB (Bypass UI)
                    proc = subprocess.Popen([ADB_PATH, "shell", "screencap", "-p"], stdout=subprocess.PIPE)
                    img_data = proc.stdout.read()
                    
                    self.wfile.write(b'--boundary\r\n')
                    self.send_header('Content-type', 'image/png')
                    self.send_header('Content-length', len(img_data))
                    self.end_headers()
                    self.wfile.write(img_data)
                    self.wfile.write(b'\r\n')
                    time.sleep(0.1) # Kontrol FPS untuk stabilitas
            except Exception as e:
                print(f"Stream interrupted: {e}")
        else:
            self.send_response(404)
            self.end_headers()

def run_phantom_bridge():
    print(f"[\033[91mPHANTOM\033[0m] Sovereign Bridge active on port {PORT}")
    print("[\033[91mPHANTOM\033[0m] Direct Kernel Access established. Bypassing HyperOS Security...")
    server = HTTPServer(('0.0.0.0', PORT), PhantomStreamHandler)
    server.serve_forever()

if __name__ == "__main__":
    # Pastikan ADB Reverse aktif untuk sinkronisasi VPS
    subprocess.run([ADB_PATH, "reverse", "tcp:8081", "tcp:8081"])
    run_phantom_bridge()
