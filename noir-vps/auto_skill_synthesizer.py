"""
auto_skill_synthesizer.py  --  NOIR SOVEREIGN AUTO-SKILL SYNTHESIZER v1.0
=========================================================================
Daemon yang memindai intel dari knowledge/intel/skills_blueprints/ secara
berkala, lalu otomatis membuat, menguji, dan men-deploy modul Python skill
baru menggunakan SkillSynthesizer.

Mode:
  python auto_skill_synthesizer.py             -- jalankan sekali
  python auto_skill_synthesizer.py --continuous -- daemon, interval 2 jam

Legal notice: Semua skill yang dihasilkan hanya boleh digunakan pada
              target authorized (lab lokal, CTF, DVWA). No unauthorized access.
"""
import os
import sys
import json
import time
import logging
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AutoSynth] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(__file__).parent.parent / "knowledge" / "autosynth.log",
            encoding="utf-8"
        )
    ]
)
log = logging.getLogger("AutoSkillSynthesizer")

BASE_DIR       = Path(__file__).parent
KNOWLEDGE_DIR  = BASE_DIR.parent / "knowledge"
BLUEPRINT_DIR  = KNOWLEDGE_DIR / "intel" / "skills_blueprints"
SKILLS_DIR     = BASE_DIR / "skills"
PROCESSED_FILE = KNOWLEDGE_DIR / "autosynth_processed.json"
RESULTS_FILE   = KNOWLEDGE_DIR / "autosynth_results.json"
CONTINUOUS_INTERVAL_HOURS = 2


def _load_processed() -> set:
    """Load hashes dari blueprint yang sudah pernah diproses."""
    if PROCESSED_FILE.exists():
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f).get("processed_hashes", []))
        except Exception:
            return set()
    return set()


def _save_processed(processed: set):
    """Simpan hashes blueprint yang sudah diproses."""
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "processed_hashes": list(processed),
            "updated_at": datetime.utcnow().isoformat()
        }, f, indent=2)


def _file_hash(path: Path) -> str:
    """SHA256 hash dari isi file untuk deteksi duplikat."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_blueprints() -> List[Dict]:
    """
    Pindai semua file JSON di BLUEPRINT_DIR dan ambil yang belum diproses.
    Mengembalikan list blueprint (dict) yang siap dikonversi ke skill.
    """
    BLUEPRINT_DIR.mkdir(parents=True, exist_ok=True)
    processed = _load_processed()
    new_blueprints = []

    for json_file in sorted(BLUEPRINT_DIR.glob("*.json")):
        file_hash = _file_hash(json_file)
        if file_hash in processed:
            continue
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for bp in data:
                    if isinstance(bp, dict):
                        bp["_source_file"] = str(json_file)
                        bp["_file_hash"]   = file_hash
                        new_blueprints.append(bp)
            elif isinstance(data, dict):
                data["_source_file"] = str(json_file)
                data["_file_hash"]   = file_hash
                new_blueprints.append(data)
        except Exception as e:
            log.warning(f"Gagal memuat {json_file.name}: {e}")

    log.info(f"Ditemukan {len(new_blueprints)} blueprint baru dari {BLUEPRINT_DIR}")
    return new_blueprints


def _build_skill_goal(blueprint: Dict) -> Optional[str]:
    """
    Mengkonversi blueprint intel menjadi kalimat goal untuk SkillSynthesizer.
    Mendukung format CVE blueprint dan MITRE TTP blueprint.
    """
    # CVE Blueprint
    if "cve_id" in blueprint:
        cve   = blueprint.get("cve_id", "Unknown CVE")
        title = blueprint.get("title", blueprint.get("description", ""))[:100]
        vuln  = blueprint.get("vulnerability_class", "injection")
        return (
            f"Buat skill Python yang mendeteksi dan melaporkan kerentanan {cve} "
            f"({vuln}): {title[:150]}. "
            f"Skill harus bisa memeriksa input/output endpoint untuk tanda-tanda "
            f"kerentanan ini dan mengembalikan laporan deteksi dalam format JSON."
        )

    # MITRE TTP Blueprint
    tid = blueprint.get("technique_id") or blueprint.get("id", "")
    if "technique_id" in blueprint or (tid and str(tid).startswith("T")):
        name  = blueprint.get("name", blueprint.get("technique_name", "Unknown Technique"))
        tactic = blueprint.get("tactic", [])
        tactic_str = ", ".join(tactic) if isinstance(tactic, list) else str(tactic)
        detect = blueprint.get("detection", "")[:200]
        return (
            f"Buat skill Python yang mengimplementasikan deteksi untuk MITRE ATT&CK "
            f"teknik {tid} '{name}' (taktik: {tactic_str}). "
            f"Gunakan petunjuk deteksi berikut: {detect}. "
            f"Skill harus menganalisis sistem lokal atau log untuk tanda-tanda TTP ini "
            f"dan mengembalikan laporan deteksi dalam format JSON."
        )

    # Generic blueprint (fallback)
    source = blueprint.get("source", "unknown")
    desc   = blueprint.get("description", blueprint.get("summary", ""))[:200]
    if desc:
        return (
            f"Buat skill Python berdasarkan blueprint keamanan [{source}]: {desc}. "
            f"Implementasikan sebagai class dengan method execute() "
            f"yang mengembalikan string hasil analisis."
        )

    return None


def _save_results(results: List[Dict]):
    """Append hasil synthesis ke file log hasil."""
    existing = []
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.extend(results)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)


def run_synthesis_cycle(max_per_cycle: int = 5) -> Dict:
    """
    Jalankan satu siklus synthesis:
    1. Scan blueprint baru dari knowledge/intel/skills_blueprints/
    2. Bangun goal dari setiap blueprint
    3. Invoke SkillSynthesizer untuk generate, audit, test, deploy skill
    4. Tandai blueprint sebagai diproses
    5. Simpan hasil ke knowledge/autosynth_results.json

    Args:
        max_per_cycle: Jumlah blueprint maksimum yang diproses per siklus.

    Returns:
        Dict berisi statistik siklus ini.
    """
    log.info("=" * 60)
    log.info("AUTO-SKILL SYNTHESIZER -- SIKLUS DIMULAI")
    log.info("=" * 60)

    blueprints = scan_blueprints()
    if not blueprints:
        log.info("Tidak ada blueprint baru. Siklus selesai.")
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

    candidates = blueprints[:max_per_cycle]
    skipped    = len(blueprints) - len(candidates)
    log.info(f"Memproses {len(candidates)} blueprint (skipped {skipped} untuk siklus berikutnya)...")

    # Import SkillSynthesizer dari modul yang sudah ada
    try:
        sys.path.insert(0, str(BASE_DIR))
        from skill_synthesizer import SkillSynthesizer
        synth = SkillSynthesizer()
    except ImportError as e:
        log.error(f"Gagal import SkillSynthesizer: {e}")
        return {"total": len(candidates), "success": 0, "failed": len(candidates), "skipped": skipped}

    processed = _load_processed()
    results   = []
    success   = 0
    failed    = 0

    for i, bp in enumerate(candidates, 1):
        file_hash   = bp.get("_file_hash", "")
        source_file = bp.get("_source_file", "unknown")
        goal = _build_skill_goal(bp)

        if not goal:
            log.warning(f"[{i}/{len(candidates)}] Blueprint tidak valid (tidak ada goal): {source_file}")
            processed.add(file_hash)
            continue

        bp_id = bp.get("cve_id") or bp.get("technique_id") or bp.get("id") or f"bp_{i}"
        log.info(f"[{i}/{len(candidates)}] Mensintesis skill untuk: {bp_id}")
        log.info(f"  Goal: {goal[:120]}...")

        try:
            result = synth.synthesize_new_skill(goal)
            result["blueprint_id"]   = bp_id
            result["source_file"]    = source_file
            result["synthesized_at"] = datetime.utcnow().isoformat()

            if result.get("success"):
                deployed = SKILLS_DIR / result.get("file", "")
                log.info(f"  [OK] Skill '{result.get('class')}' berhasil di-deploy ke {deployed}")
                success += 1
            else:
                log.warning(f"  [FAIL] {result.get('reason', 'Unknown error')}")
                failed += 1

        except Exception as e:
            log.error(f"  [ERROR] Exception saat synthesis: {e}")
            result = {"success": False, "reason": str(e), "blueprint_id": bp_id}
            failed += 1

        results.append(result)
        processed.add(file_hash)

        if i < len(candidates):
            log.info("  Jeda 3 detik sebelum blueprint berikutnya...")
            time.sleep(3)

    _save_processed(processed)
    _save_results(results)

    summary = {
        "total":     len(candidates),
        "success":   success,
        "failed":    failed,
        "skipped":   skipped,
        "timestamp": datetime.utcnow().isoformat()
    }

    log.info("=" * 60)
    log.info(f"SIKLUS SELESAI: {success} berhasil, {failed} gagal, {skipped} ditunda")
    log.info("=" * 60)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Noir Sovereign Auto-Skill Synthesizer v1.0"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help=f"Daemon mode dengan interval {CONTINUOUS_INTERVAL_HOURS} jam"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=5,
        help="Blueprint maksimum per siklus (default: 5)"
    )
    args = parser.parse_args()

    if args.continuous:
        log.info(f"Mode DAEMON aktif -- interval {CONTINUOUS_INTERVAL_HOURS} jam")
        cycle = 0
        while True:
            cycle += 1
            log.info(f"--- Daemon Cycle #{cycle} ---")
            try:
                run_synthesis_cycle(max_per_cycle=args.max)
            except Exception as e:
                log.error(f"Error di daemon cycle #{cycle}: {e}")
            log.info(f"Daemon tidur selama {CONTINUOUS_INTERVAL_HOURS} jam...")
            time.sleep(CONTINUOUS_INTERVAL_HOURS * 3600)
    else:
        summary = run_synthesis_cycle(max_per_cycle=args.max)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
