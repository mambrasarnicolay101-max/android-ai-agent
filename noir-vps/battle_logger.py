import os, json, time, logging
from datetime import datetime
from pathlib import Path

# Path setup
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "knowledge" / "battle_reports"
LOG_DIR.mkdir(exist_ok=True, parents=True)

log = logging.getLogger("BattleLogger")

class BattleLogger:
    """
    BATTLE LOGGER v1.0 — NOIR SOVEREIGN
    ==================================
    Sistem pencatatan terperinci untuk setiap simulasi serangan & pertahanan.
    Merekam metrik keberhasilan, evaluasi taktis, dan pembelajaran otonom.
    """

    @staticmethod
    def log_event(event_type: str, target: str, attacker: str, defender: str, 
                  methods: list, success: bool, findings: list, evaluation: str = None):
        """
        Mencatat laporan pertempuran lengkap.
        event_type: 'SIMULATION', 'PENTEST', 'LIVE_DEFENSE'
        """
        report_id = f"BATTLE_{int(time.time())}_{attacker[:3].upper()}"
        
        report = {
            "id": report_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "participants": {
                "attacker": attacker,
                "defender": defender,
                "target": target
            },
            "metrics": {
                "methods_tried": methods,
                "success": success,
                "penetration_rate": 1.0 if success else 0.0, # Will be more complex later
                "vulnerabilities_found": len(findings)
            },
            "raw_findings": findings,
            "evaluation": evaluation or "No manual evaluation provided.",
            "status": "COMPLETED"
        }

        # Save to JSON file
        file_path = LOG_DIR / f"{report_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        log.info(f" [BATTLE] Report generated: {report_id} | Success: {success}")

        # Index to Vector Memory for AI learning
        BattleLogger._index_to_memory(report)
        
        return report_id

    @staticmethod
    def _index_to_memory(report: dict):
        """Mengirim laporan ke Vector Memory agar AI bisa belajar secara otonom."""
        try:
            from vector_memory import vector_memory
            from ai_router import OmniRouter
            
            # Generate a summary for the memory
            summary_prompt = (
                f"Analyze this battle report and extract key tactical lessons for future self-improvement.\n"
                f"Report Data: {json.dumps(report)}\n\n"
                f"Provide a concise 'Tactical Insight' summary."
            )
            insight = OmniRouter.query(summary_prompt, task_type="reasoning")
            
            memory_text = (
                f"BATTLE REPORT {report['id']}\n"
                f"Type: {report['event_type']} | Target: {report['participants']['target']}\n"
                f"Success: {report['metrics']['success']} | Vulns Found: {report['metrics']['vulnerabilities_found']}\n"
                f"Methods: {', '.join(report['metrics']['methods_tried'])}\n"
                f"Tactical Insight: {insight}"
            )
            
            vector_memory.add_experience(
                text=memory_text,
                metadata={
                    "type": "battle_report",
                    "report_id": report["id"],
                    "success": report["metrics"]["success"],
                    "event_type": report["event_type"]
                }
            )
            log.info(f" [BATTLE] Report {report['id']} indexed into Vector Memory.")
        except Exception as e:
            log.error(f" [BATTLE] Failed to index report: {e}")

    @staticmethod
    def get_statistics():
        """Menghitung statistik keberhasilan serangan vs pertahanan."""
        reports = []
        for file in LOG_DIR.glob("*.json"):
            with open(file, "r") as f:
                reports.append(json.load(f))
        
        if not reports:
            return {"total": 0, "success_rate": 0.0}
            
        successes = len([r for r in reports if r["metrics"]["success"]])
        return {
            "total_engagements": len(reports),
            "attacker_success_rate": successes / len(reports),
            "defender_mitigation_rate": 1.0 - (successes / len(reports))
        }

if __name__ == "__main__":
    # Test logging
    BattleLogger.log_event(
        event_type="SIMULATION",
        target="DummyApp_v1",
        attacker="NeuralRedTeam",
        defender="SovereignBlueTeam",
        methods=["SQL Injection", "Command Injection"],
        success=True,
        findings=[{"type": "SQLi", "line": 27}],
        evaluation="Sistem gagal memfilter input user secara rekursif."
    )
    print(BattleLogger.get_statistics())
