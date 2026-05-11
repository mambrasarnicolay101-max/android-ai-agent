import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

# ==========================================
# NOIR SOVEREIGN: USB PC BRIDGE (pc_agent.py)
# ==========================================
# Script ini berjalan di PC Anda untuk menerima eksekusi perintah
# dari AI Agent di Android melalui kabel USB Debugging.
# 
# CARA PENGGUNAAN:
# 1. Colokkan HP ke PC dengan USB Debugging aktif.
# 2. Buka terminal PC dan jalankan: adb reverse tcp:8080 tcp:8080
# 3. Jalankan script ini: python pc_agent.py
# 4. Di HP (Aplikasi Noir Aegis), ketik chat: /pc dir
# ==========================================

PORT = 8080

class PcBridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/execute':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                cmd = payload.get('command', 'echo No command provided')
                
                print(f"[\033[95mNOIR AI\033[0m] Executing: {cmd}")
                
                # Eksekusi command di terminal PC
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                
                if not output:
                    output = "Command executed successfully (no output)."
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                res = json.dumps({"output": output[:2000]}) # Limit output to avoid crashing the bridge
                self.wfile.write(res.encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"output": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, PcBridgeHandler)
    print(f"[\033[92mREADY\033[0m] PC Bridge Listening on 127.0.0.1:{PORT}")
    print("Waiting for commands from Android Agent via USB...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()
