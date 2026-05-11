import subprocess
import os
import sys
import tempfile
import logging

log = logging.getLogger("SandboxEngine")

class SandboxEngine:
    """Mengeksekusi kode dalam lingkungan terisolasi untuk verifikasi logika."""
    
    @staticmethod
    def execute_python(code: str, timeout=5):
        """Menjalankan kode Python di sandbox dan mengembalikan output/error."""
        log.info("🧪 [Sandbox] Menjalankan verifikasi kode...")
        
        # Buat file sementara untuk kode
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tmp:
            tmp.write(code)
            tmp_path = tmp.name
            
        try:
            # Jalankan dengan batasan (bisa ditingkatkan ke Docker di Linux)
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            log.info(f"🧪 [Sandbox] Hasil Eksekusi: {'BERHASIL' if success else 'GAGAL'}")
            return {
                "success": success,
                "output": output.strip(),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            log.warning("🧪 [Sandbox] Eksekusi dihentikan: Timeout")
            return {"success": False, "error": "Timeout (Potensi Infinite Loop)"}
        except Exception as e:
            log.error(f"🧪 [Sandbox] Error Fatal: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    # Test sederhana
    test_code = "print(sum([i for i in range(100)]))"
    print(SandboxEngine.execute_python(test_code))
