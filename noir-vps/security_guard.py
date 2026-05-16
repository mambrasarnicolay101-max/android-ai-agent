import re
import logging

log = logging.getLogger("QueryGuard")

class SecurityBreachException(Exception):
    """Exception raised for detected security breaches in queries."""
    pass

class QueryGuard:
    """
    QUERY GUARD v1.0  SECURITY LAYER
    =================================
    Menangani sanitasi input dan deteksi pola SQL Injection
    tingkat lanjut untuk melindungi pilar KnowledgeBase.
    """

    @staticmethod
    def sanitize(query: str) -> str:
        """Menganalisis query untuk pola serangan yang mencurigakan."""
        if not isinstance(query, str):
            return query

        # Deteksi pola SQL Injection tingkat lanjut (Zero-day patterns)
        sql_patterns = [
            r"(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)(\s|$)",
            r"(--|#|\/\*)",
            r"('\s*OR\s*')",
            r"(WAITFOR\s+DELAY)",
            r"(BENCHMARK\(.*\))",
            r"(SLEEP\(.*\))",
            r"(GROUP\s+BY\s+.*)",
            r"(HAVING\s+.*)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                log.critical(f" [GUARD] SECURITY BREACH DETECTED: Pattern '{pattern}' found in query.")
                raise SecurityBreachException(f"Attack pattern detected: {pattern}")
        
        return query

if __name__ == "__main__":
    # Test
    try:
        QueryGuard.sanitize("SELECT * FROM users")
    except SecurityBreachException as e:
        print(f"Caught: {e}")
