import socket
import logging
import time
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [PREDATOR] %(message)s")
log = logging.getLogger("NetworkPredator")

def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, port))
        sock.close()
        if result == 0:
            return port
    except:
        pass
    return None

def scan_target(ip):
    # Common ports to hunt: HTTP(80, 8080), SSH(22), Telnet(23), SMB(445), RDP(3389)
    target_ports = [21, 22, 23, 80, 445, 3389, 8080, 8443]
    open_ports = []
    
    for port in target_ports:
        if scan_port(ip, port):
            open_ports.append(port)
            
    if open_ports:
        log.info(f"TARGET DITEMUKAN: {ip} -> Open Ports: {open_ports}")
        return {"ip": ip, "ports": open_ports}
    return None

def active_radar(subnet="192.168.1."):
    log.info(f"Menginisialisasi Radar Sibernetika pada subnet {subnet}0/24")
    log.info("Mode: Stealth (0.5s timeout/ping)")
    
    live_targets = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        # Scan dari .1 sampai .254
        for i in range(1, 255):
            ip = f"{subnet}{i}"
            futures.append(executor.submit(scan_target, ip))
            
        for future in futures:
            result = future.result()
            if result:
                live_targets.append(result)
                
    log.warning(f"Pemindaian Selesai. Menemukan {len(live_targets)} perangkat aktif dengan port terbuka.")
    return live_targets

if __name__ == "__main__":
    # Karena tidak tahu subnet pengguna secara dinamis, kita pakai default kelas C
    # Di masa depan, skrip ini bisa memanggil 'ipconfig' dan mem-parsing subnet secara otomatis.
    active_radar("192.168.1.")
