import os, sys, time, logging, json
from datetime import datetime

# Path setup
sys.path.append(os.path.dirname(__file__))
from ai_router import OmniRouter
from vector_memory import vector_memory
from evolution_engine import evolution_engine
from red_blue_arena import RedBlueArena

log = logging.getLogger("GrandSingularity")

class GrandSingularityCycle:
    """
    GRAND SINGULARITY CYCLE v1.0
    ============================
    Orkestrator kecerdasan tingkat tinggi untuk evolusi otonom 24/7.
    Mengelola siklus berpikir, belajar, simulasi, dan perbaikan diri.
    """

    def __init__(self):
        self.arena = RedBlueArena()
        self.last_rem_sleep = time.time()
        self.state_file = os.path.join(os.path.dirname(__file__), "..", "knowledge", "singularity_state.json")
        self.checkpoint_file = os.path.join(os.path.dirname(__file__), "..", "knowledge", "singularity_checkpoint.json")
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except: pass
        return {"cycle": 0, "total_evolutions": 0}

    def _save_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            log.error(f"Gagal menyimpan singularity state: {e}")

    def _load_checkpoint(self) -> dict:
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, "r") as f:
                    cp = json.load(f)
                # Only valid for current cycle
                if cp.get("cycle") == self.state.get("cycle", 0) + 1:
                    return cp
            except: pass
        return {"cycle": -1, "completed_phases": []}

    def _mark_phase_done(self, phase: str):
        cp = self._load_checkpoint()
        if cp.get("cycle") != self.state.get("cycle", 0):
            cp = {"cycle": self.state["cycle"], "completed_phases": []}
        if phase not in cp["completed_phases"]:
            cp["completed_phases"].append(phase)
        with open(self.checkpoint_file, "w") as f:
            json.dump(cp, f)

    def run_cycle(self):
        """Menjalankan satu siklus penuh evolusi otonom dengan checkpoint resume."""
        self.state["cycle"] += 1
        log.info(f" [SINGULARITY] Memulai Siklus Evolusi Agung #{self.state['cycle']}...")
        
        cp = self._load_checkpoint()
        completed = cp.get("completed_phases", [])
        
        # 1. RESEARCH & KNOWLEDGE ABSORPTION
        if "research" not in completed:
            self._step_research()
            self._mark_phase_done("research")
        else:
            log.info(" [SINGULARITY] Fase 1 (Penelitian) sudah selesai — dilanjutkan dari checkpoint.")
        
        # 2. SIMULATION & WARFARE TRAINING
        if "simulation" not in completed:
            self._step_simulation()
            self._mark_phase_done("simulation")
        else:
            log.info(" [SINGULARITY] Fase 2 (Simulasi) sudah selesai — dilanjutkan dari checkpoint.")
        
        # 3. SELF-AUDIT & HARDENING
        if "self_audit" not in completed:
            self._step_self_audit()
            self._mark_phase_done("self_audit")
        else:
            log.info(" [SINGULARITY] Fase 3 (Audit Mandiri) sudah selesai — dilanjutkan dari checkpoint.")
        
        # 4. REM SLEEP (MEMORY CONSOLIDATION)
        if time.time() - self.last_rem_sleep > 43200:  # Every 12 hours
            if "rem_sleep" not in completed:
                self._step_rem_sleep()
                self._mark_phase_done("rem_sleep")
            self.last_rem_sleep = time.time()

        # Clear checkpoint setelah siklus berhasil
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
        except: pass

        self._save_state()
        log.info(f" [SINGULARITY] Siklus #{self.state['cycle']} selesai. Hibernasi hingga jendela berikutnya.")

    def _step_research(self):
        """Tahap Penelitian: AI Interrogation & Deep Web Crawling."""
        log.info(" [SINGULARITY] Fase 1: Active AI Interrogation & Web Crawling...")
        
        # 1. Minta AI pihak ketiga untuk memikirkan topik/pertanyaan tersulit saat ini
        meta_prompt = (
            "Kamu adalah inti kognitif Noir. Hasilkan tepat 3 topik/pertanyaan spesifik dan "
            "mutakhir tentang keamanan siber, eksploitasi zero-day, atau AI evasion yang "
            "paling sulit dipecahkan tahun ini. Jawab hanya dengan format list 1, 2, 3 "
            "tanpa pembukaan/penutup."
        )
        log.info(" [SINGULARITY] Menghasilkan daftar interogasi ke OmniRouter...")
        topics_raw = OmniRouter.query(meta_prompt, task_type="reasoning")
        
        # Parsing manual
        topics = []
        if topics_raw and "[Error]" not in topics_raw:
            import re
            lines = topics_raw.split('\n')
            for line in lines:
                clean = re.sub(r'^\d+[\.\)\-]\s*', '', line.strip())
                if clean and len(clean) > 10:
                    topics.append(clean)
        
        if not topics:
            topics = ["Advanced Evasion Techniques in Python 2026", "Kernel-level Rootkits Analysis"]

        # Limit to max 3 topics per cycle
        topics = topics[:3]
        log.info(f" [SINGULARITY] Topik didapatkan: {topics}")
        
        # 2. Deep Web Crawling untuk setiap topik
        from autonomous_browser import AutonomousBrowser
        
        for topic in topics:
            log.info(f" [SINGULARITY] Memulai rayapan mendalam untuk: {topic}")
            # Crawl web dan dapatkan array dictionary {"url", "text"}
            scraped_data = AutonomousBrowser.explore_topic(topic)
            
            if not scraped_data:
                log.warning(f" [SINGULARITY] Tidak ada data web ditemukan untuk: {topic}")
                continue
                
            # 3. Lempar data mentah internet kembali ke AI Pihak Ketiga untuk ekstraksi
            log.info(" [SINGULARITY] Menganalisis hasil scraping dengan OmniRouter...")
            combined_text = "\n\n".join([f"Source: {d['url']}\n{d['text'][:1500]}" for d in scraped_data])
            
            extraction_prompt = (
                f"Topik: {topic}\n"
                f"Berikut adalah data mentah yang disedot dari internet:\n{combined_text}\n\n"
                "Ekstrak secara mendalam menjadi satu kesimpulan teknis atau cuplikan kode yang "
                "bisa langsung menjadi 'Skill/Pengetahuan' baru untukku. Fokus pada aspek paling teknikal."
            )
            
            extracted_knowledge = OmniRouter.query(extraction_prompt, task_type="coding")
            
            if extracted_knowledge and "[Error]" not in extracted_knowledge:
                vector_memory.add_experience(
                    text=f"Deep Scrape ({topic}):\n{extracted_knowledge}",
                    metadata={"source": "deep_crawler", "type": "active_learning", "topic": topic[:50]}
                )
                log.info(f" [SINGULARITY] ✔️ Pengetahuan dari '{topic[:30]}...' telah dienkripsi ke memori vektor.")

    def _step_simulation(self):
        """Tahap Simulasi: Red vs Blue Arena dengan peningkatan LLM."""
        log.info(" [SINGULARITY] Fase 2: Simulasi Perang Cyber...")
        try:
            self.arena.run_simulation()
            log.info(" [SINGULARITY] Siklus Arena Simulasi selesai.")
        except Exception as e:
            log.error(f" [SINGULARITY] Simulasi gagal: {e}")

    def _step_self_audit(self):
        """Tahap Audit Mandiri: Mencari anti-pattern dalam kode sendiri."""
        log.info(" [SINGULARITY] Fase 3: Audit-Mandiri Rekursif...")
        # Pilih file acak untuk di-audit
        core_files = ["brain.py", "ai_router.py", "sovereign_orchestrator.py", "web_server.py"]
        import random
        target = random.choice(core_files)
        target_path = os.path.join(os.path.dirname(__file__), target) if target != "web_server.py" else os.path.join(os.path.dirname(__file__), "..", "noir-ui", target)
        
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                code = f.read()
            
            prompt = f"Perform a security and performance audit on the following code. Identify potential bugs, race conditions, or security holes. Code:\n\n{code[:4000]}"
            audit_report = OmniRouter.query(prompt, task_type="coding")
            
            if audit_report and "[Error]" not in audit_report:
                evolution_engine.propose_evolution(
                    title=f"AI Self-Audit Result: {target}",
                    description=f"Automated audit findings for {target}:\n\n{audit_report}",
                    changes={"audit_findings": {"file": target, "report": audit_report}},
                    complexity=3
                )
                log.info(f" [SINGULARITY] Audit for '{target}' completed. Proposals sent to Evolution Engine.")

    def _step_rem_sleep(self):
        """Tahap REM Sleep: Mengonsolidasi memori dan menyaring pengetahuan berharga."""
        log.info(" [SINGULARITY] Phase 4: REM Sleep (Memory Consolidation)...")
        # Ambil memori terakhir dan ringkas
        memories = vector_memory.query("recent events", n_results=10)
        if memories:
            summary_prompt = f"Summarize these recent experiences into 'Core Beliefs' for the AI system. What has been learned? Memories:\n\n" + "\n".join(memories)
            summary = OmniRouter.query(summary_prompt, task_type="reasoning")
            
            if summary and "[Error]" not in summary:
                vector_memory.add_experience(
                    text=f"Core Belief Consolidation: {summary}",
                    metadata={"source": "rem_sleep", "type": "core_belief"}
                )
                log.info(" [SINGULARITY] Memory consolidation successful.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = GrandSingularityCycle()
    engine.run_cycle()
