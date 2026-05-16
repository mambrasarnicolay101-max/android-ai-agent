import os
"""
NETWORK SENTINEL v2.5  NOIR SOVEREIGN
=======================================
Pilar 6 (Upgraded): Real-time network monitoring & ACTIVE DEFENSE
- Parse SSH auth.log untuk brute-force detection
- Auto-block IP via iptables/netsh
- Honeypot Mesh (Port Jebakan)
- Automated Counter-Strike (Retaliation via Nmap)
"""
import subprocess, os, platform, logging, time, re, json, threading, socket
from collections import defaultdict

log = logging.getLogger("NetworkSentinel")

GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "http://"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")).rstrip("/")
API_KEY = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

BLOCKED_IPS_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "blocked_ips.json")
INTEL_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")

class NetworkSentinel:
    """Aegis Active Defense v2.5 - Deteksi, Blokir, & Serang Balik."""

    _blocked_ips: set = set()
    _fail_counts: dict = defaultdict(int)
    _last_audit: float = 0
    _honeypot_started = False

    @classmethod
    def load_blocked_ips(cls):
        try:
            if os.path.exists(BLOCKED_IPS_FILE):
                with open(BLOCKED_IPS_FILE, "r") as f:
                    data = json.load(f)
                    cls._blocked_ips = set(data.get("blocked", []))
        except: pass

    @classmethod
    def save_blocked_ips(cls):
        try:
            os.makedirs(os.path.dirname(BLOCKED_IPS_FILE), exist_ok=True)
            with open(BLOCKED_IPS_FILE, "w") as f:
                json.dump({"blocked": list(cls._blocked_ips), "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}, f)
        except: pass

    @staticmethod
    def counter_strike(ip: str):
        """[RETALIATION PROTOCOL] Memindai balik IP penyerang."""
        log.warning(f"[COUNTER-STRIKE] Initiating retaliation scan on {ip}...")
        try:
            # Menggunakan NMAP untuk fast port scan (Top 100 ports)
            output = subprocess.check_output(["nmap", "-F", "-Pn", ip], stderr=subprocess.DEVNULL, timeout=45).decode(errors="replace")
            
            # Simpan Intel ke file
            os.makedirs(INTEL_DIR, exist_ok=True)
            with open(os.path.join(INTEL_DIR, "counter_strike_intel.log"), "a") as f:
                f.write(f"\n--- TARGET: {ip} | TIME: {time.ctime()} ---\n{output}\n")
            
            # Tambah ke Vector Memory
            try:
                from vector_memory import vector_memory
                vector_memory.add_experience(
                    text=f"Counter-Strike Target: {ip}\nResult:\n{output}",
                    metadata={"source": "counter_strike", "type": "recon"}
                )
            except: pass
            log.info(f"[COUNTER-STRIKE] Intelijen untuk {ip} berhasil diekstrak dan diserap.")
        except Exception as e:
            log.debug(f"[COUNTER-STRIKE] Scan gagal pada {ip}: {e}")

    @staticmethod
    def start_honeypot(port=2222):
        """[HONEYPOT MESH] Membuka port palsu untuk menjebak botnet."""
        def listen():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                s.listen(5)
                log.info(f"[HONEYPOT] Jebakan aktif di port {port}.")
                while True:
                    conn, addr = s.accept()
                    ip = addr[0]
                    log.critical(f"[HONEYPOT] PENYUSUP TERTANGKAP DI PORT {port}: {ip}")
                    try:
                        # Fake SSH Banner
                        conn.send(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1\r\n")
                        conn.settimeout(3.0)
                        payload = conn.recv(1024)
                        if payload:
                            os.makedirs(INTEL_DIR, exist_ok=True)
                            with open(os.path.join(INTEL_DIR, "honeypot_payloads.log"), "a") as f:
                                f.write(f"[{time.ctime()}] IP: {ip} | Port: {port} | Payload: {payload}\n")
                    except: pass
                    finally:
                        conn.close()
                    
                    # Eksekusi blokir dan Retaliation
                    NetworkSentinel.block_ip(ip)
            except Exception as e:
                log.error(f"[HONEYPOT] Error port {port}: {e}")
        
        t = threading.Thread(target=listen, daemon=True)
        t.start()

    @staticmethod
    def _detect_bruteforce() -> list:
        suspicious = []
        fail_map = defaultdict(int)
        THRESHOLD = 5

        log_paths = ["/var/log/auth.log", "/var/log/secure", "/var/log/syslog"]
        log_path = next((p for p in log_paths if os.path.exists(p)), None)

        if not log_path:
            try:
                output = subprocess.check_output(["lastb", "--time-format", "notime"], stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace")
                for line in output.splitlines():
                    match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
                    if match: fail_map[match.group(1)] += 1
            except: return []
        else:
            try:
                output = subprocess.check_output(["tail", "-n", "5000", log_path], stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace")
                for line in output.splitlines():
                    if "Failed password" in line or "Invalid user" in line:
                        match = re.search(r"from\s+(\d{1,3}(?:\.\d{1,3}){3})", line)
                        if match: fail_map[match.group(1)] += 1
            except: return []

        for ip, count in fail_map.items():
            if count >= THRESHOLD:
                suspicious.append(ip)
                log.warning(f"[SENTINEL] Brute-force terdeteksi: {ip} ({count} attempts)")
        return suspicious

    @staticmethod
    def get_active_connections() -> list:
        conns = []
        try:
            output = subprocess.check_output(["ss", "-tnp"], stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace")
            for line in output.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 5: conns.append({"state": parts[0], "local": parts[3], "remote": parts[4]})
        except:
            try:
                output = subprocess.check_output(["netstat", "-tn"], stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace")
                for line in output.splitlines()[2:]:
                    parts = line.split()
                    if len(parts) >= 5: conns.append({"state": parts[5] if len(parts)>5 else "?", "local": parts[3], "remote": parts[4]})
            except: pass
        return conns

    @staticmethod
    def block_ip(ip: str):
        if ip in NetworkSentinel._blocked_ips: return
        system = platform.system()
        success = False
        try:
            if system == "Linux":
                subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True, timeout=5, capture_output=True)
                subprocess.run(["iptables", "-A", "OUTPUT", "-d", ip, "-j", "DROP"], check=True, timeout=5, capture_output=True)
                success = True
                log.info(f"[SENTINEL] IP {ip} diblokir via IPTables.")
            elif system == "Windows":
                rule_name = f"Noir_Aegis_{ip.replace('.', '_')}"
                subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", f"name={rule_name}", "dir=in", "action=block", f"remoteip={ip}"], check=True, timeout=5, capture_output=True)
                success = True
                log.info(f"[SENTINEL] IP {ip} diblokir via Windows Firewall.")
        except: pass

        if success:
            NetworkSentinel._blocked_ips.add(ip)
            NetworkSentinel.save_blocked_ips()
            NetworkSentinel._alert_dashboard(ip)
            
            # [ACTIVE DEFENSE] Pemicu Counter-Strike (Asynchronous)
            threading.Thread(target=NetworkSentinel.counter_strike, args=(ip,), daemon=True).start()

    @staticmethod
    def _alert_dashboard(ip: str):
        try:
            import requests
            requests.post(f"{GATEWAY}/api/logs", headers=HEADERS, json={
                "device_id": "VPS_SENTINEL",
                "level": "CRITICAL",
                "message": f" AEGIS: IP {ip} DIBLOKIR. Counter-Strike diinisiasi."
            }, timeout=5)
        except: pass

    @staticmethod
    def audit_network():
        log.info("[SENTINEL] Memulai audit keamanan jaringan v2.5...")
        
        # Inisialisasi Honeypot Ports
        if not NetworkSentinel._honeypot_started:
            NetworkSentinel.start_honeypot(port=2222) # SSH Fake Port
            NetworkSentinel.start_honeypot(port=23)   # Telnet Fake Port
            NetworkSentinel.start_honeypot(port=8080) # HTTP Proxy Fake Port
            NetworkSentinel._honeypot_started = True

        NetworkSentinel.load_blocked_ips()
        suspicious_ips = NetworkSentinel._detect_bruteforce()
        for ip in suspicious_ips:
            NetworkSentinel.block_ip(ip)

        conns = NetworkSentinel.get_active_connections()
        established = [c for c in conns if "ESTAB" in c.get("state", "")]
        return {"blocked_count": len(NetworkSentinel._blocked_ips), "threats": suspicious_ips}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    NetworkSentinel.audit_network()
    while True: time.sleep(1) # Keep alive untuk mendengarkan port Honeypot

