import os
import logging
from sandbox_engine import SandboxEngine

log = logging.getLogger("QA_Validator")

class QAValidator:
    """
    PILAR 11: QA/VALIDATOR SENTINEL
    Tugas: Memvalidasi output kode dan fungsionalitas sistem sebelum dianggap 'selesai'.
    """
    
    @staticmethod
    def validate_code(code_path: str):
        log.info(f" Validating code at: {code_path}")
        
        if not os.path.exists(code_path):
            return {"success": False, "error": "File not found"}
            
        with open(code_path, "r", encoding="utf-8") as f:
            code = f.read()
            
        # Run in sandbox
        result = SandboxEngine.execute_python(code)
        
        if result["success"]:
            log.info(f" Code at {code_path} passed validation.")
        else:
            log.warning(f" Code at {code_path} FAILED validation: {result.get('error')}")
            
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(QAValidator.validate_code("noir-vps/seed_memory.py"))
