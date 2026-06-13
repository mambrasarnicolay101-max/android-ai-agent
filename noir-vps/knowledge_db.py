import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

log = logging.getLogger("KnowledgeDB")

class SovereignDB:
    """
    Manajer Database SQLite Tersentralisasi untuk Noir Sovereign v30.0.
    Menggantikan penyimpanan JSON statis untuk performa tinggi & keamanan thread (concurrency).
    """

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "sovereign_core.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        """Mendapatkan koneksi database dengan timeout untuk penanganan konkurensi (WAL mode)."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        # Aktifkan Write-Ahead Logging untuk konkurensi tinggi
        conn.execute('pragma journal_mode=wal')
        return conn

    def _init_db(self):
        """Membuat skema tabel jika belum ada."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Tabel Blocked IPs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS blocked_ips (
                        ip TEXT PRIMARY KEY,
                        reason TEXT,
                        timestamp TEXT
                    )
                ''')

                # Tabel Honeypot Traps
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS honeypot_traps (
                        port INTEGER PRIMARY KEY,
                        protocol TEXT,
                        trap_type TEXT,
                        description TEXT,
                        active INTEGER DEFAULT 1
                    )
                ''')
                conn.commit()
                log.info("[DB] SQLite Schema initialized successfully.")
        except Exception as e:
            log.error(f"[DB] Init error: {e}")

    # ==========================================
    # BLOCKED IPs OPERATIONS
    # ==========================================
    def add_blocked_ip(self, ip: str, reason: str = "Unknown Threat"):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute('''
                    INSERT OR REPLACE INTO blocked_ips (ip, reason, timestamp)
                    VALUES (?, ?, ?)
                ''', (ip, reason, now))
                conn.commit()
        except Exception as e:
            log.error(f"[DB] add_blocked_ip error: {e}")

    def is_ip_blocked(self, ip: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM blocked_ips WHERE ip = ?', (ip,))
                return cursor.fetchone() is not None
        except Exception as e:
            log.error(f"[DB] is_ip_blocked error: {e}")
            return False

    def get_all_blocked_ips(self) -> List[Dict]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT ip, reason, timestamp FROM blocked_ips')
                rows = cursor.fetchall()
                return [{"ip": r[0], "reason": r[1], "timestamp": r[2]} for r in rows]
        except Exception:
            return []

    def remove_blocked_ip(self, ip: str):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM blocked_ips WHERE ip = ?', (ip,))
                conn.commit()
        except Exception as e:
            log.error(f"[DB] remove_blocked_ip error: {e}")

    # ==========================================
    # HONEYPOT TRAPS OPERATIONS
    # ==========================================
    def seed_default_traps(self):
        """Memasukkan trap dasar jika tabel kosong."""
        traps = [
            (21, "FTP", "ftp_decoy", "Decoy FTP Server for credential harvest"),
            (22, "SSH", "ssh_tarpit", "SSH Tarpit to stall attackers"),
            (23, "Telnet", "telnet_decoy", "Vintage protocol trap"),
            (3306, "MySQL", "mysql_honeypot", "Database exploitation trap"),
            (8080, "HTTP-Alt", "web_decoy", "Admin panel decoy")
        ]
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM honeypot_traps')
                if cursor.fetchone()[0] == 0:
                    cursor.executemany('''
                        INSERT INTO honeypot_traps (port, protocol, trap_type, description)
                        VALUES (?, ?, ?, ?)
                    ''', traps)
                    conn.commit()
        except Exception as e:
            log.error(f"[DB] seed_default_traps error: {e}")

    def get_active_traps(self) -> List[Dict]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT port, protocol, trap_type, description FROM honeypot_traps WHERE active = 1')
                rows = cursor.fetchall()
                return [{"port": r[0], "protocol": r[1], "type": r[2], "desc": r[3]} for r in rows]
        except Exception:
            return []

# Singleton instance
sovereign_db = SovereignDB()
sovereign_db.seed_default_traps()
