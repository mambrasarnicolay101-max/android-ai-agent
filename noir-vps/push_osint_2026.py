import json
import sys
import os

from cloud_memory_client import CloudMemoryClient

osint_data = {
    "web_development_trends_2026": {
        "architecture": "Coordination and intent-driven architecture, agentic workflows.",
        "meta_frameworks": "Dominance of Next.js, Nuxt; Server Actions and React Server Components standard.",
        "technologies": ["TypeScript", "WebAssembly", "PWAs", "Modern CSS (container queries, cascade layers)"],
        "performance": "Edge computing, Server-first rendering, React Compiler."
    },
    "cyber_architecture_2026": {
        "paradigm": "Cybersecurity Mesh Architecture (CSMA) replacing castle-and-moat.",
        "trust_model": "Zero Trust Architecture (ZTA), Identity as the Perimeter.",
        "ai_integration": "Agentic AI, Defensive AI, Predictive Analytics.",
        "vulnerability_mgmt": "Continuous Threat Exposure Management (CTEM).",
        "cryptography": "Quantum-Ready Infrastructure, Crypto-agile."
    },
    "web_vulnerabilities_2026": {
        "trends": [
            "AI-Driven Attack Automation (mapping, discovery, phishing)",
            "Shrinking Day-0 Timelines",
            "AI-Generated Vulnerabilities from coding assistants",
            "Identity-Centric Attacks (MFA fatigue, session hijacking)",
            "Supply Chain and SaaS Linkages"
        ],
        "top_vulnerabilities": [
            "Broken Access Control",
            "Security Misconfiguration",
            "Injection Attacks",
            "Authentication Failures",
            "Software Supply Chain Failures",
            "Cryptographic Failures"
        ]
    }
}

key = "osint_trends_2026"
client = CloudMemoryClient()
payload = json.dumps(osint_data)
success = client.push_knowledge(key, payload)

if success:
    print(f"Successfully pushed OSINT data with key: {key}")
else:
    print(f"Failed to push OSINT data with key: {key}")
