import os
import json
import time
from typing import List, Dict

class SynthesisEngine:
    """
    NEURAL MESH RECOGNITION v18.0 [SYNTHESIS]
    Role: Transforms raw research data into structured intelligence artifacts.
    """
    
    def __init__(self, workspace_dir: str = "/app/brain/synthesis"):
        self.workspace = workspace_dir
        os.makedirs(self.workspace, exist_ok=True)
        
    def generate_intelligence_report(self, topic: str, raw_data: List[Dict]) -> str:
        """Synthesizes a full markdown report from raw research bits."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"#  NOIR SOVEREIGN INTEL REPORT: {topic.upper()}\n"
        report += f"**Synthesis Date:** {timestamp}\n"
        report += f"**Classification:** OMEGA-LEVEL INTEL\n\n"
        
        report += "##  EXECUTIVE SUMMARY\n"
        report += f"Analisis otonom terhadap domain '{topic}' telah disintesis dari {len(raw_data)} sumber intelijen. "
        report += "Berikut adalah poin-poin krusial yang harus diperhatikan.\n\n"
        
        report += "##  SYNTHESIZED KNOWLEDGE BITS\n"
        for i, bit in enumerate(raw_data):
            report += f"### {i+1}. {bit.get('title', 'Knowledge Segment')}\n"
            report += f"> {bit.get('content', 'No detailed data available.')}\n\n"
            if 'source' in bit:
                report += f"**Source:** {bit['source']}\n\n"
                
        report += "##  EVOLUTIONARY RECOMMENDATION\n"
        report += "Berdasarkan sintesis data di atas, Noir merekomendasikan:\n"
        report += "- **Optimalisasi Core**: Mengintegrasikan algoritma ini ke dalam pipeline otonom.\n"
        report += "- **Mesh Sync**: Membagikan pengetahuan ini ke seluruh agen aktif dalam Neural Mesh.\n\n"
        
        report += "---\n"
        report += "*Synthesized autonomously by Noir Synthesis Engine v18.0*"
        
        # Save as artifact
        filename = f"report_{int(time.time())}.md"
        path = os.path.join(self.workspace, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
            
        return report

if __name__ == "__main__":
    # Test Synthesis
    engine = SynthesisEngine()
    test_data = [
        {"title": "Encryption Protocols", "content": "AES-256-GCM is the current standard for sovereign data protection.", "source": "Cyber-Security Database"},
        {"title": "Neural Latency", "content": "WebSocket polling at 500ms provides optimal balance for command responsiveness.", "source": "Network Diagnostics"}
    ]
    print(engine.generate_intelligence_report("System Stability", test_data))
