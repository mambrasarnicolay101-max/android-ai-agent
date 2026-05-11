"""
NETWORK SENTINEL v2.0 — NOIR SOVEREIGN
=======================================
Pilar 6 (Upgraded): Real-time network monitoring
- Parse SSH auth.log untuk brute-force detection
- Auto-block IP via iptables (Linux) / netsh (Windows)
- Bandwidth & connection anomaly detection
- Alert ke dashboard via API
"""
import subprocess, os, platform, logging, time, re, json
from collections import defaultdict

log = logging.getLogger("NetworkSentinel")

GATEWAY = os.environ.get("NOIR_GATEWAY_URL", "http://localhost:8765").rstrip("/")
API_KEY = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

BLOCKED_IPS_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "blocked_ips.json")

class NetworkSentinel:
    """Aegis Active Defense v2.0 - Deteksi & Blokir Ancaman Jaringan Secara Real-time."""

    _blocked_ips: set = set()
    _fail_counts: dict = defaultdict(int)
    _last_audit: float = 0

    @classmethod
    def load_blocked_ips(cls):
        """Load daftar IP yang sudah diblokir dari persistent storage."""
        try:
            if os.path.exists(BLOCKED_IPS_FILE):
                with open(BLOCKED_IPS_FILE, "r") as f:
                    data = json.load(f)
                    cls._blocked_ips = set(data.get("blocked", []))
                    log.info(f"[SENTINEL] Loaded {len(cls._blocked_ips)} blocked IPs from history.")
        except Exception as e:
            log.warning(f"[SENTINEL] Could not load blocked IPs: {e}")

    @classmethod
    def save_blocked_ips(cls):
        """Simpan daftar IP yang diblokir ke disk."""
        try:
            os.makedirs(os.path.dirname(BLOCKED_IPS_FILE), exist_ok=True)
            with open(BLOCKED_IPS_FILE, "w") as f:
                json.dump({"blocked": list(cls._blocked_ips), "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}, f)
        except Exception as e:
            log.warning(f"[SENTINEL] Could not save blocked IPs: {e}")

    @staticmethod
    def _detect_bruteforce() -> list:
        """Parse /var/log/auth.log untuk mendeteksi brute-force SSH."""
        suspicious = []
        fail_map = defaultdict(int)
        THRESHOLD = 5  # Lebih dari 5 kegagalan = brute-force

        log_paths = ["/var/log/auth.log", "/var/log/secure", "/var/log/syslog"]
        log_path = next((p for p in log_paths if os.path.exists(p)), None)

        if not log_path:
            # Fallback: cek via `lastb` command
            try:
                output = subprocess.check_output(["lastb", "--time-format", "notime"],
                    stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace")
                for line in output.splitlines():
                    match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", line)
                    if match:
                        ip = match.group(1)
                        fail_map[ip] += 1
            except Exception:
                return []
        else:
            try:
                # Hanya baca 5000 baris terakhir untuk efisiensi
                output = subprocess.check_output(
                    ["tail", "-n", "5000", log_path],
                    stderr=subprocess.DEVNULL, timeout=5
                ).decode(errors="replace")

                for line in output.splitlines():
                    if "Failed password" in line or "Invalid user" in line:
                        match = re.search(r"from\s+(\d{1,3}(?:\.\d{1,3}){3})", line)
                        if match:
                            ip = match.group(1)
                            fail_map[ip] += 1
            except Exception as e:
                log.debug(f"[SENTINEL] auth.log read failed: {e}")
                return []

        for ip, count in fail_map.items():
            if count >= THRESHOLD:
                suspicious.append(ip)
                log.warning(f"[SENTINEL] Brute-force terdeteksi: {ip} ({count} attempts)")

        return suspicious

    @staticmethod
    def get_active_connections() -> list:
        """Ambil daftar koneksi aktif via ss atau netstat."""
        conns = []
        try:
            output = subprocess.check_output(
                ["ss", "-tnp"], stderr=subprocess.DEVNULL, timeout=5
            ).decode(errors="replace")
            for line in output.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    conns.append({"state": parts[0], "local": parts[3], "remote": parts[4]})
        except Exception:
            try:
                output = subprocess.check_output(
                    ["netstat", "-tn"], stderr=subprocess.DEVNULL, timeout=5
                ).decode(errors="replace")
                for line in output.splitlines()[2:]:
                    parts = line.split()
                    if len(parts) >= 5:
                        conns.append({"state": parts[5] if len(parts) > 5 else "?",
                                      "local": parts[3], "remote": parts[4]})
            except Exception:
                pass
        return conns

    @staticmethod
    def block_ip(ip: str):
        """Blokir IP menggunakan firewall sistem."""
        if ip in NetworkSentinel._blocked_ips:
            log.info(f"[SENTINEL] IP {ip} sudah diblokir sebelumnya.")
            return

        system = platform.system()
        success = False
        try:
            if system == "Linux":
                subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                               check=True, timeout=5, capture_output=True)
                subprocess.run(["iptables", "-A", "OUTPUT", "-d", ip, "-j", "DROP"],
                               check=True, timeout=5, capture_output=True)
                success = True
                log.info(f"[SENTINEL] ✅ IP {ip} diblokir via IPTables.")
            elif system == "Windows":
                rule_name = f"Noir_Aegis_{ip.replace('.', '_')}"
                subprocess.run(
                    ["netsh", "advfirewall", "firewall", "add", "rule",
                     f"name={rule_name}", "dir=in", "action=block", f"remoteip={ip}"],
                    check=True, timeout=5, capture_output=True
                )
                success = True
                log.info(f"[SENTINEL] ✅ IP {ip} diblokir via Windows Firewall.")
        except Exception as e:
            log.error(f"[SENTINEL] ❌ Gagal memblokir {ip}: {e}")

        if success:
            NetworkSentinel._blocked_ips.add(ip)
            NetworkSentinel.save_blocked_ips()
            NetworkSentinel._alert_dashboard(ip)

    @staticmethod
    def _alert_dashboard(ip: str):
        """Kirim notifikasi ke dashboard bahwa IP telah diblokir."""
        try:
            import requests
            requests.post(f"{GATEWAY}/api/logs", headers=HEADERS, json={
                "device_id": "VPS_SENTINEL",
                "level": "CRITICAL",
                "message": f"🚨 AEGIS: IP {ip} DIBLOKIR otomatis karena brute-force attack."
            }, timeout=5)
        except Exception:
            pass

    @staticmethod
    def audit_network():
        """Audit lengkap: brute-force detection + connection monitoring."""
        log.info("[SENTINEL] Memulai audit keamanan jaringan v2.0...")
        NetworkSentinel.load_blocked_ips()

        # Deteksi brute-force
        suspicious_ips = NetworkSentinel._detect_bruteforce()
        for ip in suspicious_ips:
            NetworkSentinel.block_ip(ip)

        # Cek koneksi aktif untuk anomali
        conns = NetworkSentinel.get_active_connections()
        established = [c for c in conns if "ESTAB" in c.get("state", "")]
        if len(established) > 50:
            log.warning(f"[SENTINEL] Anomali: {len(established)} koneksi aktif (>50 threshold)")

        log.info(f"[SENTINEL] Audit selesai. Blocked: {len(NetworkSentinel._blocked_ips)} IPs | "
                 f"Active connections: {len(established)}")

        # Simpan ke memory
        try:
            from vector_memory import vector_memory
            vector_memory.add_experience(
                text=f"NETWORK AUDIT: {len(suspicious_ips)} threats detected, "
                     f"{len(suspicious_ips)} IPs blocked. Active connections: {len(established)}",
                metadata={"source": "network_sentinel", "type": "audit_result"}
            )
        except Exception:
            pass

        return {"blocked_count": len(NetworkSentinel._blocked_ips), "threats": suspicious_ips}
