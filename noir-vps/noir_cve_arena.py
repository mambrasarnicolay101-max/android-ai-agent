#!/usr/bin/env python3
"""
NOIR CVE ARENA v1.0 — RED-BLUE TRAINING WITH REAL CVE DATA
============================================================
Meningkatkan kemampuan Red-Blue Arena dari dummy system biasa
menjadi latihan menggunakan data kerentanan nyata dari:
  - NIST NVD (National Vulnerability Database) API v2.0
  - Exploit-DB via GHDB
  - CVE Details API

AI akan:
  1. Mengambil CVE terbaru (7 hari terakhir) yang kritis (CVSS >= 7.0)
  2. Meminta Red Team (LLM) membuat PoC exploit untuk CVE tersebut
  3. Meminta Blue Team (LLM) membuat patch/mitigasi
  4. Menyimpan semua hasil ke Vector Memory
"""
import os
import json
import time
import logging
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

log = logging.getLogger("NoirCVEArena")

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY  = os.environ.get("NVD_API_KEY", "")  # optional, rate limit lebih longgar

class NoirCVEArena:
    """
    Arena Pelatihan berdasarkan CVE nyata dari internet.
    Jauh lebih efektif daripada dummy system buatan sendiri.
    """

    def __init__(self):
        self.sandbox_dir = os.path.join(os.path.dirname(__file__), ".sandbox", "cve_arena")
        os.makedirs(self.sandbox_dir, exist_ok=True)

    # ── Pengambilan Data CVE ───────────────────────────────────────────────────
    def fetch_recent_cves(self, days: int = 7, min_cvss: float = 7.0, max_results: int = 5) -> list:
        """Ambil CVE terbaru dari NIST NVD API."""
        log.info(f"[CVE-ARENA] Mengambil CVE terbaru (CVSS >= {min_cvss}) dari NIST NVD...")
        
        end_date   = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "pubStartDate": start_date.strftime("%Y-%m-%dT00:00:00.000"),
            "pubEndDate":   end_date.strftime("%Y-%m-%dT23:59:59.999"),
            "cvssV3Severity": "HIGH" if min_cvss >= 7.0 else "MEDIUM",
            "resultsPerPage": max_results,
        }
        
        if NVD_API_KEY:
            params["apiKey"] = NVD_API_KEY
        
        url = NVD_API_BASE + "?" + urllib.parse.urlencode(params)
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NoirSovereign/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            
            cves = []
            for vuln in data.get("vulnerabilities", []):
                cve_item = vuln.get("cve", {})
                cve_id   = cve_item.get("id", "")
                desc     = ""
                for d in cve_item.get("descriptions", []):
                    if d.get("lang") == "en":
                        desc = d.get("value", "")
                        break
                
                # Ambil CVSS score
                score = 0.0
                metrics = cve_item.get("metrics", {})
                for v in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                    if v in metrics and metrics[v]:
                        score = metrics[v][0].get("cvssData", {}).get("baseScore", 0.0)
                        break
                
                if score >= min_cvss:
                    cves.append({
                        "id":          cve_id,
                        "description": desc[:1000],
                        "cvss_score":  score,
                        "published":   cve_item.get("published", ""),
                    })
            
            log.info(f"[CVE-ARENA] {len(cves)} CVE berhasil diambil.")
            return cves[:max_results]
        
        except Exception as e:
            log.error(f"[CVE-ARENA] Gagal mengambil CVE dari NVD: {e}")
            # Fallback: gunakan data CVE sample terkenal
            return self._get_fallback_cves()

    def _get_fallback_cves(self) -> list:
        """Fallback CVE klasik jika NVD API tidak dapat diakses."""
        return [
            {
                "id": "CVE-2021-44228",
                "description": "Apache Log4j2 JNDI features do not protect against attacker controlled LDAP (Log4Shell). Remote code execution via specially crafted log messages.",
                "cvss_score": 10.0,
                "published": "2021-12-10",
            },
            {
                "id": "CVE-2023-44487",
                "description": "HTTP/2 Rapid Reset Attack allows attackers to exploit the RST_STREAM feature to conduct a distributed denial of service (DDoS) attack.",
                "cvss_score": 7.5,
                "published": "2023-10-10",
            },
            {
                "id": "CVE-2024-3400",
                "description": "PAN-OS command injection vulnerability in GlobalProtect feature allows unauthenticated attackers to execute arbitrary code with root privileges.",
                "cvss_score": 10.0,
                "published": "2024-04-12",
            },
        ]

    # ── Simulasi Red vs Blue per CVE ──────────────────────────────────────────
    def simulate_cve(self, cve: dict) -> dict:
        """Jalankan satu siklus Red-Blue untuk satu CVE."""
        from ai_router import OmniRouter
        cve_id   = cve["id"]
        cve_desc = cve["description"]
        score    = cve["cvss_score"]
        
        log.info(f"[CVE-ARENA] ═══ Simulasi: {cve_id} (CVSS {score}) ═══")
        
        # ── RED TEAM: Analisis + PoC ──────────────────────────────────────────
        red_prompt = (
            f"CVE ID: {cve_id}\n"
            f"Description: {cve_desc}\n"
            f"CVSS Score: {score}\n\n"
            "As a Red Team security researcher, analyze this CVE and:\n"
            "1. Explain the root cause and attack surface\n"
            "2. Provide a conceptual Proof-of-Concept (PoC) in Python (safe, non-destructive)\n"
            "3. List the conditions required for exploitation\n"
            "Keep response technical and under 400 words."
        )
        log.info(f"[RED TEAM] Menganalisis {cve_id}...")
        red_analysis = OmniRouter.query(red_prompt, task_type="reasoning")
        
        time.sleep(2)
        
        # ── BLUE TEAM: Mitigasi + Patch ──────────────────────────────────────
        blue_prompt = (
            f"CVE ID: {cve_id}\n"
            f"Red Team Analysis: {red_analysis[:500]}\n\n"
            "As a Blue Team defender:\n"
            "1. Provide immediate mitigation steps (no reboot required)\n"
            "2. Provide a Python patch/hardening code snippet\n"
            "3. List detection rules (log patterns, IDS signatures)\n"
            "Keep response actionable and under 400 words."
        )
        log.info(f"[BLUE TEAM] Merumuskan mitigasi untuk {cve_id}...")
        blue_defense = OmniRouter.query(blue_prompt, task_type="coding")
        
        result = {
            "cve_id":        cve_id,
            "cvss_score":    score,
            "red_analysis":  red_analysis,
            "blue_defense":  blue_defense,
            "simulated_at":  datetime.now().isoformat(),
        }
        
        # ── Simpan ke file sandbox ────────────────────────────────────────────
        out_file = os.path.join(self.sandbox_dir, f"{cve_id.replace('-','_')}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        log.info(f"[CVE-ARENA] Hasil {cve_id} disimpan ke: {out_file}")
        return result

    # ── Memory & Evolution Integration ────────────────────────────────────────
    def _save_to_memory(self, result: dict):
        """Simpan hasil simulasi ke Vector Memory dan Evolution Engine."""
        try:
            from vector_memory import vector_memory
            text = (
                f"CVE Simulation: {result['cve_id']} (CVSS {result['cvss_score']})\n"
                f"Red Team:\n{result['red_analysis'][:500]}\n"
                f"Blue Team:\n{result['blue_defense'][:500]}"
            )
            vector_memory.add_experience(
                text=text,
                metadata={
                    "source": "cve_arena",
                    "type":   "cve_training",
                    "cve_id": result["cve_id"],
                    "cvss":   str(result["cvss_score"]),
                }
            )
            log.info(f"[CVE-ARENA] {result['cve_id']} tersimpan ke Vector Memory.")
        except Exception as e:
            log.warning(f"[CVE-ARENA] Gagal simpan ke memory: {e}")
        
        try:
            from evolution_engine import evolution_engine
            evolution_engine.propose_evolution(
                title=f"CVE Training: {result['cve_id']}",
                description=(
                    f"Red-Blue Arena berhasil mensimulasikan {result['cve_id']} (CVSS {result['cvss_score']}).\n"
                    f"Patch mitigasi dan pola deteksi telah dihasilkan dan disimpan."
                ),
                changes={"cve_report": result},
                complexity=3,
            )
        except Exception as e:
            log.warning(f"[CVE-ARENA] Gagal log ke evolution: {e}")

    # ── Entry Point ───────────────────────────────────────────────────────────
    def run_full_cycle(self, days: int = 7, max_cves: int = 3):
        """Jalankan satu siklus penuh CVE Arena."""
        log.info("[CVE-ARENA] ════════ SIKLUS CVE ARENA DIMULAI ════════")
        
        cves = self.fetch_recent_cves(days=days, max_results=max_cves)
        if not cves:
            log.warning("[CVE-ARENA] Tidak ada CVE yang ditemukan. Lewati siklus ini.")
            return
        
        results = []
        for cve in cves:
            try:
                r = self.simulate_cve(cve)
                self._save_to_memory(r)
                results.append(r)
                time.sleep(3)  # jeda antar CVE untuk rate limit API
            except Exception as e:
                log.error(f"[CVE-ARENA] Gagal simulasi {cve.get('id','?')}: {e}")
        
        log.info(f"[CVE-ARENA] ════════ SELESAI: {len(results)}/{len(cves)} CVE disimulasikan ════════")
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    arena = NoirCVEArena()
    arena.run_full_cycle(days=7, max_cves=2)
