import socket
import os

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def diagnose():
    print("--- NOIR SOVEREIGN DIAGNOSTIC ---")
    ports = [80, 8080, 8765, 5000]
    for p in ports:
        status = "OPEN" if check_port(p) else "CLOSED"
        print(f"Port {p}: {status}")
    
    print("\nProcesses check:")
    os.system("ps aux | grep python")

if __name__ == "__main__":
    diagnose()
