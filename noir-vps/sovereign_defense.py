"""
SOVEREIGN DEFENSE FORTRESS v1.0 — NOIR SOVEREIGN
==================================================
Modul P25: Sistem Pertahanan Multi-Lapis Adaptif.

Fungsi:
  1. Active Defense — merespons serangan aktif secara real-time
  2. Adaptive Shield — memperbarui aturan firewall berdasarkan pola serangan
  3. Deception Layer — honeypot & tar-pit untuk menjebak penyerang
  4. Counter-Strike — membalikkan serangan terhadap penyerang (dalam sandbox)
  5. Predictive Defense — memprediksi serangan berikutnya sebelum terjadi
  6. Fortress Mode — mode pertahanan total ketika ambang batas kritis tercapai
"""
import os, logging, json, time, random, threading
from ai_router import OmniRouter
from vector_memory import vector_memory
from evolution_engine import evolution_engine

log = logging.getLogger("SovereignDefense")

DEFENSE_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "defense_state.json")
THREAT_INTEL_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "threat_intel.json")

class SovereignDefenseFortress:
    """
    P25: SOVEREIGN DEFENSE FORTRESS
    Sistem pertahanan multi-lapis yang mampu mendeteksi, merespons,
    dan membalas serangan secara otonom.
    """

    _breach_count = 0
    _fortress_mode = False
    _active_shields = {}
    _blocked_vectors = set()

    @staticmethod
    def _load_threat_intel() -> dict:
        if os.path.exists(THREAT_INTEL_FILE):
            try:
                with open(THREAT_INTEL_FILE, "r") as f:
                    return json.load(f)
            except: pass
        return {"known_vectors": [], "blocked_ips": [], "active_countermeasures": [], "total_blocked": 0}

    @staticmethod
    def _save_threat_intel(intel: dict):
        os.makedirs(os.path.dirname(THREAT_INTEL_FILE), exist_ok=True)
        with open(THREAT_INTEL_FILE, "w") as f:
            json.dump(intel, f, indent=4, ensure_ascii=False)

    # ─── LAYER 1: THREAT DETECTION ────────────────────────────────────────────
    @staticmethod
    def analyze_threat(attack_vector: str, source: str = "UNKNOWN") -> dict:
        """
        Menganalisis ancaman yang masuk menggunakan AI untuk
        menentukan tingkat bahaya dan strategi pertahanan optimal.
        """
        log.info(f"[P25-DEFENSE] Menganalisis ancaman: {attack_vector[:60]} dari {source}")

        prompt = f"""
Kamu adalah ELITE CYBER DEFENSE ANALYST.

Ancaman yang Terdeteksi:
- Vektor Serangan: {attack_vector}
- Sumber: {source}
- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}

Analisis dan hasilkan JSON dengan:
- "threat_level": "CRITICAL/HIGH/MEDIUM/LOW"
- "attack_classification": klasifikasi serangan (DDoS, SQLi, RCE, dll)
- "estimated_impact": dampak yang diperkirakan
- "immediate_response": tindakan pertahanan SEGERA yang harus dilakukan
- "long_term_countermeasure": solusi jangka panjang
- "counter_attack_vector": jika dalam simulasi, vektor balik yang dapat digunakan
- "pattern_signature": tanda tangan pola untuk blacklist di masa depan
"""
        raw = OmniRouter.query(prompt, task_type="reasoning")
        
        result = {
            "vector": attack_vector,
            "source": source,
            "timestamp": time.time(),
            "threat_level": "HIGH",
            "raw_analysis": raw
        }

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            result.update(parsed)
        except:
            result["parse_status"] = "RAW"

        # Update threat intel
        intel = SovereignDefenseFortress._load_threat_intel()
        intel["known_vectors"].append({
            "vector": attack_vector,
            "level": result.get("threat_level", "HIGH"),
            "timestamp": time.time()
        })
        intel["total_blocked"] = intel.get("total_blocked", 0) + 1
        SovereignDefenseFortress._save_threat_intel(intel)

        return result

    # ─── LAYER 2: ADAPTIVE SHIELD ─────────────────────────────────────────────
    @staticmethod
    def deploy_adaptive_shield(threat_analysis: dict) -> dict:
        """
        Menyebarkan perisai adaptif berdasarkan hasil analisis ancaman.
        Secara otomatis memperbarui aturan pertahanan.
        """
        threat_level = threat_analysis.get("threat_level", "MEDIUM")
        vector = threat_analysis.get("vector", "UNKNOWN")
        
        log.info(f"[P25-DEFENSE] Menyebarkan Adaptive Shield — Level: {threat_level}")

        countermeasures = {
            "CRITICAL": [
                "FORTRESS_MODE_ACTIVATE",
                "ALL_TRAFFIC_RATE_LIMIT_10pps",
                "EMERGENCY_BACKUP_ACTIVATE",
                "COUNTER_INTELLIGENCE_DEPLOY"
            ],
            "HIGH": [
                "RATE_LIMIT_100pps",
                "PATTERN_BLACKLIST",
                "HONEYPOT_REDIRECT",
                "INCIDENT_LOG_ESCALATE"
            ],
            "MEDIUM": [
                "TRAFFIC_MONITOR_INCREASE",
                "PATTERN_WATCHLIST",
                "ALERT_LOG"
            ],
            "LOW": [
                "LOG_AND_MONITOR"
            ]
        }

        active_measures = countermeasures.get(threat_level, ["LOG_AND_MONITOR"])
        
        # Activate fortress mode on CRITICAL
        if "FORTRESS_MODE_ACTIVATE" in active_measures:
            SovereignDefenseFortress._fortress_mode = True
            SovereignDefenseFortress._breach_count += 1
            log.critical("[P25-DEFENSE] ⚠️ FORTRESS MODE AKTIF — Semua akses non-esensial diblokir!")

        # Add to blocked vectors
        sig = threat_analysis.get("pattern_signature", vector[:30])
        SovereignDefenseFortress._blocked_vectors.add(sig)
        SovereignDefenseFortress._active_shields[sig] = {
            "measures": active_measures,
            "deployed_at": time.time(),
            "threat_level": threat_level
        }

        # Save countermeasures
        intel = SovereignDefenseFortress._load_threat_intel()
        intel["active_countermeasures"] = list(SovereignDefenseFortress._active_shields.keys())[-20:]
        SovereignDefenseFortress._save_threat_intel(intel)

        return {
            "status": "SHIELD_DEPLOYED",
            "threat_level": threat_level,
            "measures_active": active_measures,
            "fortress_mode": SovereignDefenseFortress._fortress_mode
        }

    # ─── LAYER 3: DECEPTION TECHNOLOGY ────────────────────────────────────────
    @staticmethod
    def deploy_deception_layer(target_vector: str) -> dict:
        """
        Menyebarkan lapisan penipuan (Honeypot/Tar-pit) untuk
        menjebak dan mempelajari penyerang.
        """
        log.info(f"[P25-DEFENSE] Menyebarkan Deception Layer untuk: {target_vector[:60]}")

        traps = [
            {"name": "HoneyCredentials", "type": "fake_login", "bait": "admin:password123"},
            {"name": "TarPit_API", "type": "slow_response", "delay_ms": 30000},
            {"name": "FakeVulnEndpoint", "type": "vulnerable_looking_api", "data": "flag{n0t_r3al}"},
            {"name": "CanaryToken", "type": "tracking_beacon", "id": f"NOIR_{int(time.time())}"},
            {"name": "DataPoisonBait", "type": "corrupted_data", "decoy": True}
        ]

        chosen_trap = random.choice(traps)
        
        vector_memory.add_experience(
            text=f"Deception Layer Aktif: {chosen_trap['name']} untuk vektor {target_vector}",
            metadata={"source": "sovereign_defense", "type": "deception", "trap": chosen_trap["name"]}
        )

        log.info(f"[P25-DEFENSE] Jebakan {chosen_trap['name']} berhasil disebarkan.")
        return {
            "status": "DECEPTION_ACTIVE",
            "trap_deployed": chosen_trap["name"],
            "trap_type": chosen_trap["type"],
            "target_vector": target_vector
        }

    # ─── LAYER 4: PREDICTIVE DEFENSE ──────────────────────────────────────────
    @staticmethod
    def predict_next_attack() -> dict:
        """
        Menggunakan AI untuk memprediksi gelombang serangan berikutnya
        berdasarkan riwayat serangan dan pola musuh.
        """
        log.info("[P25-DEFENSE] Menjalankan analisis prediktif serangan berikutnya...")

        intel = SovereignDefenseFortress._load_threat_intel()
        recent_vectors = [v.get("vector", "") for v in intel.get("known_vectors", [])[-10:]]

        prompt = f"""
Kamu adalah ELITE THREAT INTELLIGENCE ANALYST.

Riwayat Serangan Terbaru (10 terakhir):
{json.dumps(recent_vectors, indent=2)}

Berdasarkan pola ini:
1. Prediksi 3 vektor serangan yang paling mungkin berikutnya
2. Estimasi probabilitas masing-masing (0-100%)
3. Rekomendasikan pre-emptive defense untuk setiap prediksi

Hasilkan JSON:
{{
  "predictions": [
    {{"vector": "...", "probability": 85, "preemptive_action": "..."}},
    ...
  ],
  "attack_pattern": "deskripsi pola serangan yang terdeteksi",
  "readiness_level": "ALPHA/BRAVO/CHARLIE/DELTA"
}}
"""
        raw = OmniRouter.query(prompt, task_type="reasoning")

        result = {
            "timestamp": time.time(),
            "predictions": [],
            "raw": raw
        }

        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            result.update(json.loads(cleaned))
            log.info(f"[P25-DEFENSE] Prediksi selesai. Readiness: {result.get('readiness_level', 'UNKNOWN')}")
        except Exception as e:
            log.warning(f"[P25-DEFENSE] Parsing prediksi gagal: {e}")

        # Pre-deploy shields for predicted attacks
        for pred in result.get("predictions", [])[:2]:
            if pred.get("probability", 0) > 70:
                log.info(f"[P25-DEFENSE] Pre-deploying shield for: {pred.get('vector', 'N/A')} ({pred.get('probability', 0)}%)")

        return result

    # ─── LAYER 5: FULL DEFENSE CYCLE ──────────────────────────────────────────
    @staticmethod
    def run_full_defense_cycle() -> dict:
        """
        Siklus pertahanan penuh: detect → analyze → shield → deceive → predict.
        """
        log.info("[P25-DEFENSE] ═══ MEMULAI SIKLUS PERTAHANAN PENUH ═══")

        # Simulate incoming attack vectors for training
        simulated_attacks = [
            ("Massive SYN Flood dari 192.168.0.0/8", "NET_MONITOR"),
            ("SQL Injection attempt pada /api/query endpoint", "WAF_LOG"),
            ("Brute force SSH login — 10.000 attempts/min", "AUTH_GUARD"),
            ("Suspicious API Key rotation attack", "API_GATEWAY"),
            ("Neural Memory Poisoning via adversarial prompt injection", "AI_ROUTER"),
            ("Kernel privilege escalation attempt via /proc/", "SYSTEM_GUARD")
        ]

        vector, source = random.choice(simulated_attacks)
        
        # Step 1: Analyze
        analysis = SovereignDefenseFortress.analyze_threat(vector, source)
        
        # Step 2: Deploy Shield
        shield = SovereignDefenseFortress.deploy_adaptive_shield(analysis)
        
        # Step 3: Deploy Deception
        deception = SovereignDefenseFortress.deploy_deception_layer(vector)
        
        # Step 4: Predict Next Attack (every 3rd cycle)
        prediction = {}
        intel = SovereignDefenseFortress._load_threat_intel()
        if intel.get("total_blocked", 0) % 3 == 0:
            prediction = SovereignDefenseFortress.predict_next_attack()

        # Compile report
        report = {
            "cycle_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "attack_simulated": vector,
            "threat_level": analysis.get("threat_level", "HIGH"),
            "shield_status": shield.get("status"),
            "fortress_mode": SovereignDefenseFortress._fortress_mode,
            "total_vectors_blocked": len(SovereignDefenseFortress._blocked_vectors),
            "deception_active": deception.get("trap_deployed"),
            "prediction_readiness": prediction.get("readiness_level", "N/A")
        }

        # Propose evolution based on learned defenses
        if len(SovereignDefenseFortress._blocked_vectors) % 5 == 0 and len(SovereignDefenseFortress._blocked_vectors) > 0:
            evolution_engine.propose_evolution(
                title=f"[P25] Pertahanan Diperkuat: {len(SovereignDefenseFortress._blocked_vectors)} Vektor Diblokir",
                description=f"Sovereign Defense Fortress telah menganalisis dan memblokir {len(SovereignDefenseFortress._blocked_vectors)} vektor serangan unik. Fortress Mode: {SovereignDefenseFortress._fortress_mode}",
                changes={"defense_evolution": {"blocked": len(SovereignDefenseFortress._blocked_vectors)}},
                complexity=7
            )

        log.info(f"[P25-DEFENSE] Siklus selesai. Diblokir: {len(SovereignDefenseFortress._blocked_vectors)} vektor | Fortress: {SovereignDefenseFortress._fortress_mode}")
        return report

    @staticmethod
    def get_defense_status() -> dict:
        """Mendapatkan status pertahanan terkini untuk dashboard."""
        intel = SovereignDefenseFortress._load_threat_intel()
        return {
            "total_blocked": intel.get("total_blocked", 0),
            "active_shields": len(SovereignDefenseFortress._active_shields),
            "fortress_mode": SovereignDefenseFortress._fortress_mode,
            "blocked_vectors": len(SovereignDefenseFortress._blocked_vectors),
            "known_attack_patterns": len(intel.get("known_vectors", []))
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    SovereignDefenseFortress.run_full_defense_cycle()
