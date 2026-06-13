"""
SkillT1056001Keylogging -- Noir Sovereign Security Skill
Auto-generated from MITRE ATT&CK blueprint: T1056.001
Source: MITRE_ATTCK | Generated: 2026-06-13T19:19:20.382397

Technique: Keylogging
Tactics: collection, credential-access
Platforms: Linux, macOS, Network Devices, Windows
"""
import os
import sys
import json
import logging
import subprocess
import platform
from pathlib import Path
from typing import List, Dict

log = logging.getLogger("SkillT1056001Keylogging")


class SkillT1056001Keylogging:
    """
    MITRE ATT&CK Detection Skill: T1056.001 - Keylogging
    Tactics: collection, credential-access
    
    Detection guidance: 
    
    LEGAL NOTE: Hanya digunakan untuk analisis defensive pada sistem sendiri.
    """

    TECHNIQUE_ID = "T1056.001"
    TECHNIQUE_NAME = "Keylogging"
    TACTICS = ["collection", "credential-access"]
    PLATFORMS = ["Linux", "macOS", "Network Devices", "Windows"]
    DETECTION_HINTS = ["suspicious", "unauthorized", "anomaly"]

    def __init__(self):
        self.findings = []
        self.log = logging.getLogger(self.__class__.__name__)
        self.os_type = platform.system().lower()

    def _run_command(self, cmd: List[str], timeout: int = 10) -> str:
        """Jalankan perintah sistem dan kembalikan output."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=timeout, encoding="utf-8", errors="ignore"
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

    def _check_processes(self) -> List[Dict]:
        """Periksa proses yang berjalan untuk tanda-tanda TTP ini."""
        suspicious = []
        if self.os_type == "windows":
            output = self._run_command(["tasklist", "/fo", "csv", "/v"])
        else:
            output = self._run_command(["ps", "aux"])

        lines = output.split("\n")
        for line in lines:
            for hint in self.DETECTION_HINTS:
                if hint.lower() in line.lower():
                    suspicious.append({"line": line[:200], "matched_hint": hint})
                    break

        return suspicious

    def _check_startup_items(self) -> List[str]:
        """Periksa startup items untuk persistensi (Windows)."""
        items = []
        if self.os_type != "windows":
            return items
        output = self._run_command([
            "reg", "query",
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        ])
        return [line.strip() for line in output.split("\n") if line.strip()]

    def _check_network_connections(self) -> List[str]:
        """Periksa koneksi jaringan aktif."""
        if self.os_type == "windows":
            output = self._run_command(["netstat", "-an"])
        else:
            output = self._run_command(["netstat", "-an"])
        return [line for line in output.split("\n") if "ESTABLISHED" in line or "LISTEN" in line]

    def execute(self) -> str:
        """Jalankan deteksi TTP T1056.001 dan kembalikan laporan JSON."""
        self.log.info(f"[{self.TECHNIQUE_ID}] Menjalankan deteksi: {self.TECHNIQUE_NAME}")

        processes = self._check_processes()
        startup   = self._check_startup_items()
        network   = self._check_network_connections()[:20]

        risk = "HIGH" if processes else ("MEDIUM" if startup else "LOW")

        report = {
            "technique_id":   self.TECHNIQUE_ID,
            "technique_name": self.TECHNIQUE_NAME,
            "tactics":        self.TACTICS,
            "os":             platform.system(),
            "hostname":       platform.node(),
            "risk_level":     risk,
            "suspicious_processes": processes[:10],
            "startup_items_count": len(startup),
            "active_connections":  len(network),
            "recommendation":  "Investigasi proses mencurigakan yang ditemukan" if processes else "Tidak ada indikasi aktif",
            "disclaimer":      "DEFENSIVE USE ONLY - AUTHORIZED SYSTEMS"
        }

        self.log.info(f"Deteksi selesai: {risk} risk, {len(processes)} proses mencurigakan")
        return json.dumps(report, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import unittest

    class TestSkillT1056001Keylogging(unittest.TestCase):
        def test_initialization(self):
            skill = SkillT1056001Keylogging()
            self.assertEqual(skill.TECHNIQUE_ID, "T1056.001")
            self.assertIsInstance(skill.TACTICS, list)

        def test_execute_returns_json(self):
            skill = SkillT1056001Keylogging()
            result = skill.execute()
            parsed = json.loads(result)
            self.assertIn("technique_id", parsed)
            self.assertIn("risk_level", parsed)

        def test_check_processes_returns_list(self):
            skill = SkillT1056001Keylogging()
            result = skill._check_processes()
            self.assertIsInstance(result, list)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSkillT1056001Keylogging)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
