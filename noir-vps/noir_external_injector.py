#!/usr/bin/env python3
"""
NOIR EXTERNAL INJECTOR v1.0 — ANTI-ECHO-CHAMBER ENGINE
========================================================
Mencegah echo-chamber dengan menyuntikkan data NYATA dari dunia luar
ke dalam setiap siklus evolusi:

  1. GitHub Trending — Teknologi & arsitektur terpopuler hari ini
  2. NIST NVD — CVE kritis terbaru (real-world attack patterns)
  3. CTF Challenges — PicoCTF, CTFtime (tantangan terverifikasi)
  4. Security News — Berita keamanan siber terkini
  5. ArXiv Papers — Riset akademik terbaru tentang AI & security
"""
import json
import time
import logging
import urllib.request
import urllib.parse
import urllib.error
import re
from datetime import datetime, timedelta
from pathlib import Path

log = logging.getLogger("ExternalInjector")

INJECT_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "external_feed"
INJECT_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = INJECT_DIR / "injection_cache.json"
CACHE_TTL  = 3600  # 1 jam

_cache = {}

def _load_cache():
    global _cache
    if CACHE_FILE.exists():
        try:
            _cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            _cache = {}

def _save_cache():
    CACHE_FILE.write_text(json.dumps(_cache, indent=2, ensure_ascii=False), encoding="utf-8")

def _http_get(url: str, headers: dict = None, timeout: int = 15) -> str:
    """HTTP GET dengan handling sederhana."""
    try:
        req = urllib.request.Request(url,
                                     headers={**(headers or {}),
                                              "User-Agent": "NoirSovereign/1.0 Research-Bot"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        log.warning(f"[INJECT] HTTP {e.code} untuk {url[:60]}")
        return ""
    except Exception as e:
        log.warning(f"[INJECT] Error fetch {url[:60]}: {e}")
        return ""


class NoirExternalInjector:
    """
    Menyuntikkan keberagaman pengetahuan eksternal ke dalam setiap
    siklus evolusi untuk mencegah echo-chamber dan stagnasi.
    """

    def __init__(self):
        _load_cache()

    def _cached(self, key: str, fetch_fn, ttl: int = CACHE_TTL):
        """Cache result dari fungsi fetch."""
        entry = _cache.get(key)
        if entry and time.time() - entry.get("ts", 0) < ttl:
            log.info(f"[INJECT] Cache hit: {key}")
            return entry["data"]
        result = fetch_fn()
        _cache[key] = {"ts": time.time(), "data": result}
        _save_cache()
        return result

    # ── 1. GitHub Trending ────────────────────────────────────────────────────
    def fetch_github_trending(self, language: str = "", since: str = "daily") -> list:
        """Ambil repositori trending dari GitHub."""
        log.info("[INJECT] Fetching GitHub Trending...")

        def _fetch():
            url = f"https://api.github.com/search/repositories?q=stars:>100+created:>{(datetime.utcnow()-timedelta(days=7)).strftime('%Y-%m-%d')}&sort=stars&order=desc&per_page=10"
            if language:
                url += f"+language:{urllib.parse.quote(language)}"
            text = _http_get(url, headers={"Accept": "application/vnd.github.v3+json"})
            if not text:
                return []
            try:
                data = json.loads(text)
                return [
                    {
                        "name":        r.get("full_name"),
                        "description": r.get("description", "")[:200],
                        "language":    r.get("language"),
                        "stars":       r.get("stargazers_count"),
                        "topics":      r.get("topics", []),
                        "url":         r.get("html_url"),
                    }
                    for r in data.get("items", [])
                ]
            except Exception as e:
                log.error(f"[INJECT] GitHub parse error: {e}")
                return []

        return self._cached(f"github_trending_{language}", _fetch)

    # ── 2. NIST NVD CVE Feed ──────────────────────────────────────────────────
    def fetch_critical_cves(self, days: int = 3, max_count: int = 5) -> list:
        """Ambil CVE kritis terbaru dari NIST NVD."""
        log.info("[INJECT] Fetching Critical CVEs from NIST NVD...")

        def _fetch():
            end   = datetime.utcnow()
            start = end - timedelta(days=days)
            url = (
                "https://services.nvd.nist.gov/rest/json/cves/2.0"
                f"?pubStartDate={start.strftime('%Y-%m-%dT00:00:00.000')}"
                f"&pubEndDate={end.strftime('%Y-%m-%dT23:59:59.999')}"
                f"&cvssV3Severity=CRITICAL&resultsPerPage={max_count}"
            )
            text = _http_get(url)
            if not text:
                return []
            try:
                data  = json.loads(text)
                cves  = []
                for v in data.get("vulnerabilities", []):
                    c    = v.get("cve", {})
                    desc = next((d["value"] for d in c.get("descriptions", []) if d["lang"] == "en"), "")
                    score = 0.0
                    for mk in ["cvssMetricV31", "cvssMetricV30"]:
                        mlist = c.get("metrics", {}).get(mk, [])
                        if mlist:
                            score = mlist[0].get("cvssData", {}).get("baseScore", 0.0)
                            break
                    cves.append({
                        "id":          c.get("id"),
                        "description": desc[:500],
                        "cvss":        score,
                        "published":   c.get("published", ""),
                    })
                return cves
            except Exception as e:
                log.error(f"[INJECT] NVD parse error: {e}")
                return []

        return self._cached(f"cves_{days}d", _fetch, ttl=1800)

    # ── 3. ArXiv Security & AI Papers ─────────────────────────────────────────
    def fetch_arxiv_papers(self, query: str = "AI agent security autonomous", max_count: int = 5) -> list:
        """Ambil paper akademik terbaru dari ArXiv."""
        log.info(f"[INJECT] Fetching ArXiv papers: '{query}'...")

        def _fetch():
            encoded = urllib.parse.quote(query)
            url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&sortBy=submittedDate&sortOrder=descending&max_results={max_count}"
            text = _http_get(url)
            if not text:
                return []
            papers = []
            entries = re.findall(r'<entry>(.*?)</entry>', text, re.DOTALL)
            for e in entries:
                title   = re.search(r'<title>(.*?)</title>', e, re.DOTALL)
                summary = re.search(r'<summary>(.*?)</summary>', e, re.DOTALL)
                arxiv_id= re.search(r'<id>(.*?)</id>', e)
                papers.append({
                    "title":   title.group(1).strip().replace('\n', ' ') if title else "",
                    "summary": (summary.group(1).strip()[:300] if summary else ""),
                    "url":     arxiv_id.group(1).strip() if arxiv_id else "",
                })
            return papers

        return self._cached(f"arxiv_{hash(query)}", _fetch, ttl=7200)

    # ── 4. Security News (via CISA Advisories) ────────────────────────────────
    def fetch_security_news(self) -> list:
        """Ambil advisori keamanan terbaru dari CISA."""
        log.info("[INJECT] Fetching CISA Security Advisories...")

        def _fetch():
            url  = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
            text = _http_get(url, timeout=20)
            if not text:
                return []
            try:
                data   = json.loads(text)
                vulns  = data.get("vulnerabilities", [])
                recent = sorted(vulns, key=lambda x: x.get("dateAdded", ""), reverse=True)[:5]
                return [
                    {
                        "cve":         v.get("cveID"),
                        "vendor":      v.get("vendorProject"),
                        "product":     v.get("product"),
                        "description": v.get("shortDescription", "")[:300],
                        "action":      v.get("requiredAction", ""),
                        "date_added":  v.get("dateAdded"),
                    }
                    for v in recent
                ]
            except Exception as e:
                log.error(f"[INJECT] CISA parse error: {e}")
                return []

        return self._cached("cisa_kev", _fetch, ttl=3600)

    # ── 5. CTF Challenges (via CTFtime API) ───────────────────────────────────
    def fetch_ctf_challenges(self) -> list:
        """Ambil CTF events aktif dari CTFtime."""
        log.info("[INJECT] Fetching CTF Events...")

        def _fetch():
            now  = int(time.time())
            week = now + 7 * 86400
            url  = f"https://ctftime.org/api/v1/events/?limit=5&start={now}&finish={week}"
            text = _http_get(url, headers={"Accept": "application/json"})
            if not text:
                return []
            try:
                events = json.loads(text)
                return [
                    {
                        "name":   e.get("title"),
                        "format": e.get("format"),
                        "start":  e.get("start"),
                        "url":    e.get("url"),
                        "weight": e.get("weight", 0),
                    }
                    for e in events
                ]
            except Exception as e:
                log.error(f"[INJECT] CTFtime parse error: {e}")
                return []

        return self._cached("ctf_events", _fetch, ttl=3600)

    # ── Master: Ambil Semua Injeksi ───────────────────────────────────────────
    def collect_all(self) -> dict:
        """Kumpulkan semua data eksternal sekaligus untuk satu siklus."""
        log.info("[INJECT] ═══ Mengumpulkan semua data eksternal ═══")
        result = {
            "timestamp":       datetime.now().isoformat(),
            "github_trending": self.fetch_github_trending(),
            "critical_cves":   self.fetch_critical_cves(),
            "arxiv_papers":    self.fetch_arxiv_papers(),
            "security_news":   self.fetch_security_news(),
            "ctf_events":      self.fetch_ctf_challenges(),
        }

        # Simpan snapshot ke file untuk referensi
        snap_file = INJECT_DIR / f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        snap_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        log.info(f"[INJECT] Snapshot tersimpan: {snap_file.name}")

        return result

    def summarize_for_prompt(self, injection: dict) -> str:
        """Ubah data eksternal menjadi konteks singkat untuk prompt LLM."""
        lines = ["=== EXTERNAL INTELLIGENCE BRIEF ===", ""]

        # GitHub
        gh = injection.get("github_trending", [])
        if gh:
            lines.append("🔥 TRENDING TECH (GitHub):")
            for r in gh[:3]:
                lines.append(f"  • {r['name']} ({r['language']}) — {r['description'][:80]}")
            lines.append("")

        # CVEs
        cves = injection.get("critical_cves", [])
        if cves:
            lines.append("🚨 CRITICAL CVEs (Last 3 days):")
            for c in cves[:3]:
                lines.append(f"  • {c['id']} [CVSS {c['cvss']}] — {c['description'][:120]}")
            lines.append("")

        # ArXiv
        papers = injection.get("arxiv_papers", [])
        if papers:
            lines.append("📚 LATEST RESEARCH (ArXiv):")
            for p in papers[:2]:
                lines.append(f"  • {p['title'][:80]}: {p['summary'][:100]}")
            lines.append("")

        # CISA
        news = injection.get("security_news", [])
        if news:
            lines.append("⚠️ ACTIVELY EXPLOITED (CISA KEV):")
            for n in news[:2]:
                lines.append(f"  • {n['cve']} [{n['vendor']}/{n['product']}]: {n['description'][:100]}")
            lines.append("")

        lines.append("=" * 40)
        return "\n".join(lines)


injector = NoirExternalInjector()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    print("=== NoirExternalInjector Self-Test ===\n")
    inj = NoirExternalInjector()
    data = inj.collect_all()
    print(f"GitHub: {len(data['github_trending'])} repos")
    print(f"CVEs:   {len(data['critical_cves'])} entries")
    print(f"ArXiv:  {len(data['arxiv_papers'])} papers")
    print(f"CISA:   {len(data['security_news'])} advisories")
    print(f"CTF:    {len(data['ctf_events'])} events")
    print("\n" + inj.summarize_for_prompt(data))
