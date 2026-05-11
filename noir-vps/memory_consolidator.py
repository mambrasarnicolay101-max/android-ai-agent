"""
MEMORY CONSOLIDATOR v2.0 — NOIR SOVEREIGN
==========================================
Pilar 8 (Upgraded): REM Sleep + Core Beliefs + Cross-Skill Linking
"""
import logging, time, json, os
from ai_router import AIRouter
from vector_memory import vector_memory

log = logging.getLogger("MemoryConsolidator")
BELIEFS_FILE = os.path.join(os.path.dirname(__file__), "..", "knowledge", "core_beliefs.json")

class MemoryConsolidator:

    @staticmethod
    def load_core_beliefs() -> list:
        try:
            if os.path.exists(BELIEFS_FILE):
                with open(BELIEFS_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    @staticmethod
    def save_core_beliefs(beliefs: list):
        try:
            os.makedirs(os.path.dirname(BELIEFS_FILE), exist_ok=True)
            with open(BELIEFS_FILE, "w") as f:
                json.dump(beliefs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log.warning(f"[MEMORY] Gagal simpan: {e}")

    @staticmethod
    def run_rem_sleep():
        log.info("[REM Sleep v2.0] Konsolidasi memori dimulai...")
        try:
            # FIX C-03: vector_memory.query() mengembalikan string, bukan list.
            # Split berdasarkan separator ChromaDB join agar dapat diiterasi dengan benar.
            raw = vector_memory.query("learned information knowledge security programming", n_results=20)
            recent = [doc.strip() for doc in raw.split("\n") if doc.strip()] if raw else []
            if len(recent) < 3:
                log.info("[REM Sleep] Belum cukup memori untuk konsolidasi.")
                return

            existing = MemoryConsolidator.load_core_beliefs()
            beliefs_txt = "\n".join([f"- {b['belief']}" for b in existing[-10:]]) or "Belum ada."
            mem_txt = "\n".join([f"- {m}" for m in recent])

            prompt = f"""Analisis jejak memori dan ekstrak 3 Core Beliefs baru.
MEMORI: {mem_txt}
BELIEFS LAMA: {beliefs_txt}
Output: JSON array [{{"belief":"...","domain":"programming/security/general","confidence":0.8}}]"""

            raw = AIRouter.smart_query(prompt)
            new_beliefs = []
            try:
                s, e = raw.find("["), raw.rfind("]") + 1
                if s >= 0 and e > s:
                    for item in json.loads(raw[s:e]):
                        if isinstance(item, dict) and "belief" in item:
                            new_beliefs.append({**item, "formed_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
            except Exception:
                new_beliefs = [{"belief": raw[:250], "domain": "general",
                                "confidence": 0.5, "formed_at": time.strftime("%Y-%m-%dT%H:%M:%S")}]

            if new_beliefs:
                all_b = (existing + new_beliefs)[-100:]
                MemoryConsolidator.save_core_beliefs(all_b)
                for b in new_beliefs:
                    vector_memory.add_experience(
                        text=f"CORE BELIEF [{b.get('domain','general').upper()}]: {b['belief']}",
                        metadata={"source": "rem_sleep", "type": "core_belief"}
                    )
                log.info(f"[REM Sleep] {len(new_beliefs)} Core Beliefs baru terbentuk.")
        except Exception as e:
            log.error(f"[REM Sleep] Gagal: {e}")

    @staticmethod
    def cross_link_skills():
        log.info("[MEMORY] Cross-Skill Linking...")
        try:
            prog = vector_memory.query("programming algorithm optimization", n_results=5)
            sec = vector_memory.query("security vulnerability defense", n_results=5)
            if not prog or not sec:
                return
            prompt = f"Hubungkan: PROGRAMMING={str(prog[:2])} / SECURITY={str(sec[:2])}. Insight (max 150 kata)."
            insight = AIRouter.smart_query(prompt)
            if insight:
                vector_memory.add_experience(
                    text=f"CROSS-DOMAIN INSIGHT: {insight}",
                    metadata={"source": "cross_link", "type": "meta_learning"}
                )
                log.info(f"[MEMORY] Cross-link tersimpan.")
        except Exception as e:
            log.error(f"[MEMORY] Cross-link gagal: {e}")

    @staticmethod
    def run_full_consolidation():
        MemoryConsolidator.run_rem_sleep()
        MemoryConsolidator.cross_link_skills()
        log.info("[MEMORY] Konsolidasi penuh selesai.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    MemoryConsolidator.run_full_consolidation()
