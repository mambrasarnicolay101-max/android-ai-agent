import os
import logging
import json
from ai_router import OmniRouter

log = logging.getLogger("ThirdPartyTools")

class ThirdPartyAITools:
    """
    KUMPULAN TOOLS AI PIHAK KETIGA
    ==============================
    Membungkus API dari Gemini, Groq, dan DuckDuckGo menjadi 
    tools fungsional yang dapat dipanggil oleh pilar mana pun.
    """

    @staticmethod
    def analyze_vision(image_base64: str, query: str = "Describe what is happening in this screenshot.") -> str:
        """Menganalisis gambar menggunakan Gemini Vision."""
        log.info(" [TOOL] Using Gemini Vision for image analysis...")
        return OmniRouter.query_gemini(query, image_base64=image_base64)

    @staticmethod
    def deep_security_reasoning(vulnerability_report: str) -> str:
        """Analisis keamanan mendalam menggunakan Llama-3.3 (Groq)."""
        log.info(" [TOOL] Using Groq Llama-3.3 for security reasoning...")
        prompt = f"Perform a deep forensic analysis on this security report and suggest a hardening strategy:\n\n{vulnerability_report}"
        return OmniRouter.query_deepseek(prompt)

    @staticmethod
    def global_intelligence_search(topic: str) -> str:
        """Melakukan riset web real-time menggunakan DuckDuckGo."""
        log.info(f" [TOOL] Searching global intelligence for: {topic}...")
        return OmniRouter.web_search(topic)

    @staticmethod
    def code_synthesis(requirement: str) -> str:
        """Sintesis kode tingkat tinggi menggunakan model terbaik yang tersedia."""
        log.info(" [TOOL] Synthesizing complex code structure...")
        # Fallback logic: Try OpenRouter if available, else Groq
        return OmniRouter.query_deepseek(f"Generate high-quality Python code for: {requirement}")

if __name__ == "__main__":
    # Test Search Tool
    print(ThirdPartyAITools.global_intelligence_search("Latest Android zero-day 2025"))
