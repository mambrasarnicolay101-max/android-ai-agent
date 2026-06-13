#!/usr/bin/env python3
"""
NOIR KNOWLEDGE ENGINE v2.0 — SOVEREIGN MASS INTELLIGENCE SYSTEM
================================================================
Mesin pengumpulan pengetahuan masif, multi-threaded, unstoppable.
Sumber resmi & legal:
  1. GitHub API         — Repos trending: security, AI, hacking-tools
  2. NIST NVD           — Database CVE kritis & CVSS
  3. MITRE ATT&CK       — Framework TTP (Tactics, Techniques, Procedures)
  4. ArXiv              — Paper akademik AI + security terbaru
  5. CISA KEV           — Known Exploited Vulnerabilities (wajib ditambal)
  6. Sigma Rules (GitHub) — Detection rules komunitas defender
  7. CTFtime API        — Daftar CTF legal yang aktif & upcoming
  8. HackTheBox          — Machines & challenges (authorized)
  9. PortSwigger Labs    — Web security labs (authorized)
 10. OWASP Resources    — Panduan & cheat-sheets resmi

Output:
  - knowledge/intel/      : Data mentah terstruktur
  - knowledge/skills/     : Blueprint skill yang siap disintesis
  - knowledge/digest.md   : Ringkasan harian untuk dashboard
"""

import json
import time
import logging
import threading
import urllib.request
import urllib.parse
import urllib.error
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable

# ── Setup Logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NOIR-KE] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("knowledge_engine.log", encoding="utf-8")
    ]
)
log = logging.getLogger("NoirKnowledgeEngine")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent / "knowledge"
INTEL_DIR   = BASE_DIR / "intel"
SKILLS_DIR  = BASE_DIR / "skills"
DIGEST_FILE = BASE_DIR / "digest.md"
CACHE_FILE  = BASE_DIR / "ke_cache.json"

for d in [INTEL_DIR, SKILLS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Cache System ──────────────────────────────────────────────────────────────
_cache: Dict = {}
_cache_lock = threading.Lock()

def _load_cache():
    global _cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
            log.info(f"Cache dimuat: {len(_cache)} entri")
        except Exception:
            _cache = {}

def _save_cache():
    with _cache_lock:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log.warning(f"Cache save error: {e}")

def _cached(key: str, fetch_fn: Callable, ttl: int = 3600) -> Any:
    with _cache_lock:
        entry = _cache.get(key)
    if entry and (time.time() - entry.get("ts", 0)) < ttl:
        return entry["data"]
    result = fetch_fn()
    with _cache_lock:
        _cache[key] = {"ts": time.time(), "data": result}
    _save_cache()
    return result

# ── GitHub Auth Token ─────────────────────────────────────────────────────────
# Token diperlukan untuk meningkatkan rate limit GitHub API dari 60 → 5000 req/jam
GITHUB_TOKEN = "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"

# ── HTTP Client ───────────────────────────────────────────────────────────────
def _http_get(url: str, headers: dict = None, timeout: int = 20) -> str:
    try:
        # Auto-inject GitHub token untuk semua request ke api.github.com
        base_headers = {"User-Agent": "NoirSovereign-KnowledgeEngine/2.0 (Research; Legal)"}
        if "api.github.com" in url or "raw.githubusercontent.com" in url:
            base_headers["Authorization"] = f"token {GITHUB_TOKEN}"
        req = urllib.request.Request(
            url,
            headers={**base_headers, **(headers or {})}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        log.warning(f"HTTP {e.code} -> {url[:70]}")
        return ""
    except Exception as e:
        log.warning(f"Fetch error [{url[:60]}]: {e}")
        return ""

def _save_intel(category: str, name: str, data: Any) -> Path:
    """Simpan data intel ke disk."""
    cat_dir = INTEL_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r'[^\w\-]', '_', name)[:50]
    file_path = cat_dir / f"{safe_name}_{ts}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return file_path


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMBER 1: GITHUB TRENDING SECURITY/AI REPOS
# ═══════════════════════════════════════════════════════════════════════════════
class GitHubIngestor:
    TOPICS = [
        "security", "penetration-testing", "ctf", "cybersecurity",
        "threat-intelligence", "malware-analysis", "osint",
        "machine-learning", "artificial-intelligence", "llm",
        "autonomous-agent", "red-team", "blue-team", "siem",
        "vulnerability-scanner", "exploit", "fuzzing"
    ]
    LANGUAGES = ["python", "go", "rust", "c", "bash"]

    def fetch_trending_repos(self) -> List[Dict]:
        log.info("[GitHub] Fetching trending security/AI repositories...")
        results = []
        since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        for topic in self.TOPICS:
            key = f"gh_topic_{topic}"
            def _fetch(t=topic, s=since):
                url = (
                    f"https://api.github.com/search/repositories"
                    f"?q=topic:{t}+stars:>50+created:>{s}"
                    f"&sort=stars&order=desc&per_page=5"
                )
                text = _http_get(url, headers={"Accept": "application/vnd.github.v3+json"})
                if not text:
                    return []
                try:
                    data = json.loads(text)
                    return [
                        {
                            "name":        r.get("full_name"),
                            "description": (r.get("description") or "")[:300],
                            "language":    r.get("language"),
                            "stars":       r.get("stargazers_count"),
                            "topics":      r.get("topics", []),
                            "url":         r.get("html_url"),
                            "readme_url":  f"https://raw.githubusercontent.com/{r.get('full_name')}/HEAD/README.md",
                        }
                        for r in data.get("items", [])
                    ]
                except Exception:
                    return []
            data = _cached(key, _fetch, ttl=7200)
            results.extend(data)
            time.sleep(0.5)  # rate limit gentlemen

        # Fetch README untuk repo paling relevan
        top_repos = sorted(results, key=lambda x: x.get("stars", 0), reverse=True)[:20]
        for repo in top_repos:
            readme = _http_get(repo["readme_url"], timeout=10)
            if readme:
                repo["readme_snippet"] = readme[:1000]

        saved = _save_intel("github", "trending_repos", top_repos)
        log.info(f"[GitHub] {len(top_repos)} repos disimpan -> {saved}")
        return top_repos

    def fetch_sigma_rules(self) -> List[Dict]:
        """Fetch Sigma detection rules dari SigmaHQ (komunitas defender)."""
        log.info("[GitHub] Fetching Sigma Rules (Detection Engineering)...")
        key = "sigma_rules_index"
        def _fetch():
            # Sigma Rules index dari SigmaHQ
            url = "https://api.github.com/repos/SigmaHQ/sigma/contents/rules/windows"
            text = _http_get(url, headers={"Accept": "application/vnd.github.v3+json"})
            if not text:
                return []
            try:
                items = json.loads(text)
                return [{"name": i["name"], "url": i["download_url"]} for i in items[:10] if i.get("type") == "dir"]
            except Exception:
                return []
        rules_dirs = _cached(key, _fetch, ttl=86400)
        saved = _save_intel("sigma_rules", "windows_rule_dirs", rules_dirs)
        log.info(f"[Sigma] {len(rules_dirs)} kategori rules ditemukan")
        return rules_dirs

    def fetch_payloads_reference(self) -> Dict:
        """Fetch table of contents dari PayloadsAllTheThings sebagai referensi."""
        log.info("[GitHub] Fetching PayloadsAllTheThings reference...")
        key = "patt_readme"
        def _fetch():
            url = "https://raw.githubusercontent.com/swisskyrepo/PayloadsAllTheThings/master/README.md"
            text = _http_get(url)
            if not text:
                return {}
            # Extract kategori dari README
            categories = re.findall(r'##\s+(.+)', text)
            return {
                "source": "PayloadsAllTheThings",
                "url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
                "categories": categories[:50],
                "license": "MIT",
                "note": "Reference only - educational payload catalog"
            }
        data = _cached(key, _fetch, ttl=86400)
        _save_intel("github", "payloads_reference", data)
        return data


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMBER 2: NIST NVD — CVE DATABASE
# ═══════════════════════════════════════════════════════════════════════════════
class NVDIngestor:
    def fetch_critical_cves(self, days: int = 7, limit: int = 20) -> List[Dict]:
        log.info(f"[NVD] Fetching CRITICAL CVEs dari {days} hari terakhir...")
        key = f"nvd_critical_{days}d"
        def _fetch():
            end   = datetime.utcnow()
            start = end - timedelta(days=days)
            url = (
                "https://services.nvd.nist.gov/rest/json/cves/2.0"
                f"?pubStartDate={start.strftime('%Y-%m-%dT00:00:00.000')}"
                f"&pubEndDate={end.strftime('%Y-%m-%dT23:59:59.999')}"
                f"&cvssV3Severity=CRITICAL&resultsPerPage={limit}"
            )
            text = _http_get(url, timeout=30)
            if not text:
                return []
            try:
                data = json.loads(text)
                result = []
                for v in data.get("vulnerabilities", []):
                    c    = v.get("cve", {})
                    desc = next((d["value"] for d in c.get("descriptions", []) if d["lang"] == "en"), "")
                    score, vector = 0.0, ""
                    for mk in ["cvssMetricV31", "cvssMetricV30"]:
                        mlist = c.get("metrics", {}).get(mk, [])
                        if mlist:
                            score  = mlist[0].get("cvssData", {}).get("baseScore", 0.0)
                            vector = mlist[0].get("cvssData", {}).get("vectorString", "")
                            break
                    cwe = [w.get("description", [{}])[0].get("value", "") for w in c.get("weaknesses", [])]
                    result.append({
                        "id":          c.get("id"),
                        "published":   c.get("published", ""),
                        "description": desc[:600],
                        "cvss_score":  score,
                        "cvss_vector": vector,
                        "cwe":         cwe,
                        "refs":        [r.get("url") for r in c.get("references", [])[:3]],
                    })
                return sorted(result, key=lambda x: x["cvss_score"], reverse=True)
            except Exception as e:
                log.error(f"[NVD] Parse error: {e}")
                return []
        data = _cached(key, _fetch, ttl=3600)
        saved = _save_intel("cve", f"critical_cves_{days}d", data)
        log.info(f"[NVD] {len(data)} CVE kritis disimpan -> {saved}")
        return data


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMBER 3: MITRE ATT&CK FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════
class MITREIngestor:
    def fetch_techniques(self) -> Dict:
        log.info("[MITRE] Fetching ATT&CK Enterprise techniques...")
        key = "mitre_attack_enterprise"
        def _fetch():
            url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
            text = _http_get(url, timeout=60)
            if not text:
                return {}
            try:
                data  = json.loads(text)
                objs  = data.get("objects", [])
                techs = [
                    {
                        "id":          o.get("external_references", [{}])[0].get("external_id", ""),
                        "name":        o.get("name"),
                        "description": (o.get("description") or "")[:400],
                        "tactic":      [p.get("phase_name") for p in o.get("kill_chain_phases", [])],
                        "platforms":   o.get("x_mitre_platforms", []),
                        "detection":   (o.get("x_mitre_detection") or "")[:300],
                    }
                    for o in objs
                    if o.get("type") == "attack-pattern" and not o.get("revoked", False)
                ]
                return {
                    "total":      len(techs),
                    "techniques": techs[:100],  # Top 100
                    "fetched_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                log.error(f"[MITRE] Parse error: {e}")
                return {}
        data = _cached(key, _fetch, ttl=86400)
        if data:
            saved = _save_intel("mitre", "attack_enterprise_techniques", data)
            log.info(f"[MITRE] {data.get('total',0)} teknik ATT&CK disimpan -> {saved}")
        return data


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMBER 4: ARXIV — PAPER AKADEMIK AI + SECURITY
# ═══════════════════════════════════════════════════════════════════════════════
class ArXivIngestor:
    QUERIES = [
        "autonomous AI security agent",
        "large language model cybersecurity",
        "automated vulnerability detection neural",
        "adversarial machine learning attack defense",
        "zero-day vulnerability prediction",
        "threat intelligence automation",
        "penetration testing reinforcement learning",
        "AI red team autonomous",
    ]

    def fetch_papers(self) -> List[Dict]:
        log.info(f"[ArXiv] Fetching {len(self.QUERIES)} query streams...")
        all_papers = []
        for query in self.QUERIES:
            key = f"arxiv_{hashlib.md5(query.encode()).hexdigest()[:8]}"
            def _fetch(q=query):
                url = (
                    f"https://export.arxiv.org/api/query"
                    f"?search_query=all:{urllib.parse.quote(q)}"
                    f"&sortBy=submittedDate&sortOrder=descending&max_results=5"
                )
                text = _http_get(url)
                if not text:
                    return []
                entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
                results = []
                for e in entries:
                    title   = re.search(r'<title>(.*?)</title>', e, re.DOTALL)
                    summary = re.search(r'<summary>(.*?)</summary>', e, re.DOTALL)
                    arxiv_id= re.search(r'<id>(.*?)</id>', e)
                    authors = re.findall(r'<name>(.*?)</name>', e)
                    results.append({
                        "query":   q,
                        "title":   (title.group(1).strip().replace('\n', ' ') if title else ""),
                        "summary": (summary.group(1).strip()[:500] if summary else ""),
                        "url":     (arxiv_id.group(1).strip() if arxiv_id else ""),
                        "authors": authors[:3],
                    })
                return results
            papers = _cached(key, _fetch, ttl=7200)
            all_papers.extend(papers)
            time.sleep(0.3)

        saved = _save_intel("arxiv", "security_ai_papers", all_papers)
        log.info(f"[ArXiv] {len(all_papers)} paper disimpan -> {saved}")
        return all_papers


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMBER 5: CISA KNOWN EXPLOITED VULNERABILITIES
# ═══════════════════════════════════════════════════════════════════════════════
class CISAIngestor:
    def fetch_kev(self) -> List[Dict]:
        log.info("[CISA] Fetching Known Exploited Vulnerabilities catalog...")
        key = "cisa_kev"
        def _fetch():
            url  = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
            text = _http_get(url, timeout=30)
            if not text:
                return []
            try:
                data  = json.loads(text)
                vulns = data.get("vulnerabilities", [])
                recent = sorted(vulns, key=lambda x: x.get("dateAdded", ""), reverse=True)[:30]
                return [
                    {
                        "cve":         v.get("cveID"),
                        "date_added":  v.get("dateAdded"),
                        "vendor":      v.get("vendorProject"),
                        "product":     v.get("product"),
                        "description": v.get("shortDescription", "")[:400],
                        "action":      v.get("requiredAction", ""),
                        "due_date":    v.get("dueDate", ""),
                    }
                    for v in recent
                ]
            except Exception as e:
                log.error(f"[CISA] Parse error: {e}")
                return []
        data = _cached(key, _fetch, ttl=3600)
        saved = _save_intel("cisa", "known_exploited_vulns", data)
        log.info(f"[CISA] {len(data)} KEV disimpan -> {saved}")
        return data


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMBER 6: CTF LEGAL — CTFtime API
# ═══════════════════════════════════════════════════════════════════════════════
class CTFIngestor:
    def fetch_upcoming_ctfs(self) -> List[Dict]:
        log.info("[CTF] Fetching upcoming CTF events dari CTFtime...")
        key = "ctftime_upcoming"
        def _fetch():
            now = int(time.time())
            end = now + (30 * 24 * 3600)  # 30 hari ke depan
            url = f"https://ctftime.org/api/v1/events/?limit=20&start={now}&finish={end}"
            text = _http_get(url, headers={"Accept": "application/json"})
            if not text:
                return []
            try:
                events = json.loads(text)
                return [
                    {
                        "title":      e.get("title"),
                        "url":        e.get("url"),
                        "ctftime":    e.get("ctftime_url"),
                        "format":     e.get("format"),
                        "start":      e.get("start"),
                        "finish":     e.get("finish"),
                        "weight":     e.get("weight"),
                        "organizers": [o.get("name") for o in e.get("organizers", [])],
                        "tags":       e.get("tags", []),
                    }
                    for e in events
                ]
            except Exception as e:
                log.error(f"[CTF] Parse error: {e}")
                return []
        data = _cached(key, _fetch, ttl=3600)
        saved = _save_intel("ctf", "upcoming_events", data)
        log.info(f"[CTF] {len(data)} event mendatang disimpan -> {saved}")
        return data

    def fetch_ctf_writeups_topics(self) -> List[Dict]:
        """Fetch trending CTF writeup topik dari GitHub."""
        log.info("[CTF] Fetching CTF writeup repositories...")
        key = "ctf_writeups_github"
        def _fetch():
            url = (
                "https://api.github.com/search/repositories"
                "?q=ctf+writeup+topic:ctf&sort=stars&order=desc&per_page=15"
            )
            text = _http_get(url, headers={"Accept": "application/vnd.github.v3+json"})
            if not text:
                return []
            try:
                data = json.loads(text)
                return [
                    {
                        "name":        r.get("full_name"),
                        "description": (r.get("description") or "")[:200],
                        "stars":       r.get("stargazers_count"),
                        "url":         r.get("html_url"),
                        "updated":     r.get("updated_at"),
                    }
                    for r in data.get("items", [])
                ]
            except Exception:
                return []
        data = _cached(key, _fetch, ttl=14400)
        _save_intel("ctf", "writeup_repos", data)
        return data


# ═══════════════════════════════════════════════════════════════════════════════
#  SUMBER 7: OWASP RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════
class OWASPIngestor:
    CHEAT_SHEETS = [
        "Authentication_Cheat_Sheet",
        "SQL_Injection_Prevention_Cheat_Sheet",
        "XSS_Prevention_Cheat_Sheet",
        "CSRF_Prevention_Cheat_Sheet",
        "Injection_Prevention_Cheat_Sheet",
        "Input_Validation_Cheat_Sheet",
        "Session_Management_Cheat_Sheet",
        "API_Security_Cheat_Sheet",
    ]

    def fetch_cheat_sheets(self) -> List[Dict]:
        log.info(f"[OWASP] Fetching {len(self.CHEAT_SHEETS)} cheat sheets...")
        results = []
        base = "https://raw.githubusercontent.com/OWASP/CheatSheetSeries/master/cheatsheets"
        for sheet in self.CHEAT_SHEETS:
            key = f"owasp_cs_{sheet}"
            def _fetch(s=sheet):
                url  = f"{base}/{s}.md"
                text = _http_get(url)
                if not text:
                    return {}
                return {
                    "name":    s,
                    "url":     f"https://cheatsheetseries.owasp.org/cheatsheets/{s}.html",
                    "content": text[:3000],
                    "length":  len(text),
                }
            data = _cached(key, _fetch, ttl=86400)
            if data:
                results.append(data)
            time.sleep(0.2)

        saved = _save_intel("owasp", "cheat_sheets", results)
        log.info(f"[OWASP] {len(results)} cheat sheets disimpan -> {saved}")
        return results


# ═══════════════════════════════════════════════════════════════════════════════
#  SKILL BLUEPRINT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════
class SkillBlueprintGenerator:
    """
    Mengonversi data intel menjadi blueprint skill yang dapat dipelajari Noir.
    """

    def generate_from_cve(self, cves: List[Dict]) -> List[Dict]:
        blueprints = []
        for cve in cves[:10]:
            bp = {
                "type":        "defensive_blueprint",
                "source":      "NVD_CVE",
                "cve_id":      cve.get("id"),
                "skill_name":  f"Understand_{cve.get('id','unknown')}",
                "objective":   f"Learn defense pattern for {cve.get('id')} (CVSS: {cve.get('cvss_score')})",
                "description": cve.get("description", "")[:400],
                "cvss":        cve.get("cvss_score"),
                "vector":      cve.get("cvss_vector"),
                "practice_on": "HackTheBox / local lab ONLY",
                "generated":   datetime.utcnow().isoformat(),
            }
            blueprints.append(bp)
        saved = _save_intel("skills_blueprints", "cve_defense_skills", blueprints)
        log.info(f"[Blueprint] {len(blueprints)} CVE defense blueprint -> {saved}")
        return blueprints

    def generate_from_mitre(self, mitre_data: Dict) -> List[Dict]:
        techs = mitre_data.get("techniques", [])
        blueprints = []
        for t in techs[:30]:
            bp = {
                "type":       "ttp_blueprint",
                "source":     "MITRE_ATTCK",
                "tech_id":    t.get("id"),
                "tech_name":  t.get("name"),
                "tactics":    t.get("tactic"),
                "platforms":  t.get("platforms"),
                "objective":  f"Understand TTP {t.get('id')}: {t.get('name')}",
                "detection":  t.get("detection"),
                "practice":   "Local VM lab / TryHackMe / HTB ONLY",
                "generated":  datetime.utcnow().isoformat(),
            }
            blueprints.append(bp)
        saved = _save_intel("skills_blueprints", "mitre_ttp_blueprints", blueprints)
        log.info(f"[Blueprint] {len(blueprints)} MITRE TTP blueprint -> {saved}")
        return blueprints

    def generate_ctf_training_plan(self, ctfs: List[Dict], writeups: List[Dict]) -> Dict:
        plan = {
            "title":       "Noir CTF Training Plan",
            "generated":   datetime.utcnow().isoformat(),
            "platforms":   [
                {"name": "HackTheBox",  "url": "https://www.hackthebox.com", "type": "authorized"},
                {"name": "TryHackMe",   "url": "https://tryhackme.com",      "type": "authorized"},
                {"name": "PicoCTF",     "url": "https://picoctf.org",        "type": "authorized"},
                {"name": "CTFlearn",    "url": "https://ctflearn.com",        "type": "authorized"},
                {"name": "OverTheWire", "url": "https://overthewire.org",    "type": "authorized"},
                {"name": "DVWA (Local)","url": "localhost",                   "type": "local_only"},
            ],
            "upcoming_events": ctfs[:5],
            "study_repos":     writeups[:5],
            "skill_tracks": [
                "Web Exploitation (SQLi, XSS, CSRF, SSRF, XXE)",
                "Binary Exploitation (Buffer Overflow, ROP Chains)",
                "Reverse Engineering (Ghidra, IDA, radare2)",
                "Cryptography (RSA, AES, Hash Collisions)",
                "Forensics (Memory Dumps, Network Captures, Steganography)",
                "OSINT (Passive Recon, Social Engineering Awareness)",
                "Network Pentesting (Nmap, Nessus, Burp Suite — authorized targets only)",
            ]
        }
        saved = _save_intel("ctf", "training_plan", plan)
        log.info(f"[Blueprint] CTF Training Plan disimpan -> {saved}")
        return plan


# ═══════════════════════════════════════════════════════════════════════════════
#  DIGEST GENERATOR — RINGKASAN HARIAN
# ═══════════════════════════════════════════════════════════════════════════════
def generate_digest(
    github_repos, cves, mitre_data, papers, cisa_kev,
    ctfs, blueprints_cve, blueprints_mitre, ctf_plan
) -> str:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# NOIR KNOWLEDGE DIGEST",
        f"**Generated:** {now}",
        f"**Status:** SOVEREIGN_MASTER | UNSTOPPABLE LEARNING MODE",
        "",
        "---",
        "",
        f"## GitHub Intelligence ({len(github_repos)} repos ingested)",
    ]
    for r in github_repos[:5]:
        lines.append(f"- **[{r.get('name')}]({r.get('url')})** ({r.get('stars','?')} ⭐) — {r.get('description','')[:100]}")

    lines += [
        "", f"## Critical CVEs ({len(cves)} new)",
    ]
    for c in cves[:5]:
        lines.append(f"- `{c.get('id')}` CVSS:{c.get('cvss_score')} — {c.get('description','')[:100]}")

    lines += [
        "", f"## CISA Known Exploited ({len(cisa_kev)} entries)",
    ]
    for k in cisa_kev[:5]:
        lines.append(f"- `{k.get('cve')}` [{k.get('vendor')} {k.get('product')}] Added:{k.get('date_added')}")

    lines += [
        "", f"## MITRE ATT&CK ({mitre_data.get('total',0)} techniques)",
        f"- Ingested {len(blueprints_mitre)} TTP blueprints for study",
    ]

    lines += [
        "", f"## ArXiv Papers ({len(papers)} papers)",
    ]
    for p in papers[:5]:
        lines.append(f"- [{p.get('title','?')[:80]}]({p.get('url')}) — {p.get('summary','')[:100]}")

    lines += [
        "", f"## CTF Training ({len(ctfs)} upcoming events)",
        f"**Platforms (AUTHORIZED ONLY):**",
    ]
    for plat in ctf_plan.get("platforms", []):
        lines.append(f"- {plat['name']} ({plat['type']}) — {plat['url']}")

    lines += [
        "", f"## Skills Generated",
        f"- {len(blueprints_cve)} CVE Defense Blueprints",
        f"- {len(blueprints_mitre)} MITRE TTP Blueprints",
        f"- {len(ctf_plan.get('skill_tracks',[]))} Skill Tracks (CTF)",
        "",
        "---",
        "> *All knowledge is for DEFENSIVE & EDUCATIONAL purposes. Practice only on authorized platforms.*",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENGINE — ORCHESTRATOR MASIF MULTI-THREAD
# ═══════════════════════════════════════════════════════════════════════════════
class NoirKnowledgeEngine:
    def __init__(self):
        self.github = GitHubIngestor()
        self.nvd    = NVDIngestor()
        self.mitre  = MITREIngestor()
        self.arxiv  = ArXivIngestor()
        self.cisa   = CISAIngestor()
        self.ctf    = CTFIngestor()
        self.owasp  = OWASPIngestor()
        self.bp_gen = SkillBlueprintGenerator()
        _load_cache()

    def run_full_ingest(self, max_workers: int = 8) -> Dict:
        log.info("=" * 70)
        log.info("  NOIR KNOWLEDGE ENGINE v2.0 — FULL INGEST INITIATED")
        log.info("=" * 70)
        start_time = time.time()

        # Jalankan semua ingestor secara paralel
        tasks = {
            "github_repos":   self.github.fetch_trending_repos,
            "sigma_rules":    self.github.fetch_sigma_rules,
            "payloads_ref":   self.github.fetch_payloads_reference,
            "cves":           self.nvd.fetch_critical_cves,
            "mitre":          self.mitre.fetch_techniques,
            "papers":         self.arxiv.fetch_papers,
            "cisa_kev":       self.cisa.fetch_kev,
            "ctf_events":     self.ctf.fetch_upcoming_ctfs,
            "ctf_writeups":   self.ctf.fetch_ctf_writeups_topics,
            "owasp_sheets":   self.owasp.fetch_cheat_sheets,
        }

        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fn): key for key, fn in tasks.items()}
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                    log.info(f"[OK] {key} selesai")
                except Exception as e:
                    log.error(f"[FAIL] {key}: {e}")
                    results[key] = []

        # Generate blueprints dari data yang sudah dikumpulkan
        log.info("[Blueprint] Generating skill blueprints...")
        results["bp_cve"]   = self.bp_gen.generate_from_cve(results.get("cves", []))
        results["bp_mitre"] = self.bp_gen.generate_from_mitre(results.get("mitre", {}))
        results["ctf_plan"] = self.bp_gen.generate_ctf_training_plan(
            results.get("ctf_events", []),
            results.get("ctf_writeups", [])
        )

        # Generate digest
        log.info("[Digest] Generating daily digest...")
        digest = generate_digest(
            results.get("github_repos", []),
            results.get("cves", []),
            results.get("mitre", {}),
            results.get("papers", []),
            results.get("cisa_kev", []),
            results.get("ctf_events", []),
            results.get("bp_cve", []),
            results.get("bp_mitre", []),
            results.get("ctf_plan", {}),
        )
        DIGEST_FILE.write_text(digest, encoding="utf-8")

        elapsed = time.time() - start_time
        summary = {
            "status":         "COMPLETE",
            "elapsed_seconds": round(elapsed, 2),
            "github_repos":   len(results.get("github_repos", [])),
            "cves":           len(results.get("cves", [])),
            "mitre_techs":    results.get("mitre", {}).get("total", 0),
            "papers":         len(results.get("papers", [])),
            "cisa_kev":       len(results.get("cisa_kev", [])),
            "ctf_events":     len(results.get("ctf_events", [])),
            "owasp_sheets":   len(results.get("owasp_sheets", [])),
            "bp_cve":         len(results.get("bp_cve", [])),
            "bp_mitre":       len(results.get("bp_mitre", [])),
            "digest":         str(DIGEST_FILE),
        }

        log.info("=" * 70)
        log.info(f"  INGEST COMPLETE in {elapsed:.1f}s")
        log.info(f"  GitHub: {summary['github_repos']} repos | CVEs: {summary['cves']} | MITRE: {summary['mitre_techs']} techs")
        log.info(f"  Papers: {summary['papers']} | CTF: {summary['ctf_events']} events | OWASP: {summary['owasp_sheets']} sheets")
        log.info(f"  Blueprints: {summary['bp_cve']} (CVE) + {summary['bp_mitre']} (MITRE)")
        log.info("=" * 70)

        _save_intel("summary", f"ingest_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}", summary)
        return summary

    def run_continuous(self, interval_hours: float = 6.0):
        """Loop otonom: ingest ulang setiap N jam tanpa henti."""
        log.info(f"[Engine] CONTINUOUS MODE aktif (interval={interval_hours}h)")
        cycle = 0
        while True:
            cycle += 1
            log.info(f"[Engine] ══ SIKLUS #{cycle} DIMULAI ══")
            try:
                summary = self.run_full_ingest()
                log.info(f"[Engine] Siklus #{cycle} selesai. Tidur {interval_hours}h...")
            except Exception as e:
                log.error(f"[Engine] Siklus #{cycle} error: {e}. Retry dalam 30 menit...")
                time.sleep(1800)
                continue
            time.sleep(interval_hours * 3600)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    engine = NoirKnowledgeEngine()

    if "--continuous" in sys.argv:
        # Mode daemon: jalan terus menerus setiap 6 jam
        engine.run_continuous(interval_hours=6.0)
    else:
        # Mode single-shot: satu kali ingest penuh
        summary = engine.run_full_ingest()
        print("\n" + "=" * 60)
        print("  HASIL INGEST:")
        print("=" * 60)
        for k, v in summary.items():
            print(f"  {k:<25}: {v}")
        print("=" * 60)
