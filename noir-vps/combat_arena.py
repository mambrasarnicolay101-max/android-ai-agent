import subprocess
import time
import os
import logging
from pathlib import Path

log = logging.getLogger("CombatArena")

class CombatArena:
    """
    Mengelola eksekusi nyata dari sistem rentan dan script eksploit.
    Bertindak sebagai ring tinju (sandbox) untuk OPS 1 (Target) vs OPS 2 (Exploit).
    """
    def __init__(self, sandbox_dir: Path):
        self.sandbox_dir = sandbox_dir
        self.target_process = None
        self.target_port = 5000

    def start_target_server(self, code: str, filename: str = "server.py") -> tuple[bool, str]:
        """Menjalankan server web rentan di background."""
        self.stop_target_server() # Pastikan port bersih sebelum mulai
        
        target_path = self.sandbox_dir / filename
        target_path.write_text(code, encoding="utf-8")
        
        log.info(f"[ARENA] Memulai target server ({filename}) pada port {self.target_port}...")
        
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PORT": str(self.target_port)}
        self.target_process = subprocess.Popen(
            ["python", str(target_path)],
            cwd=str(self.sandbox_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Beri waktu server untuk booting (3 detik)
        time.sleep(3)
        
        # Cek apakah server langsung crash (syntax error, dsb)
        if self.target_process.poll() is not None:
            stdout, stderr = self.target_process.communicate()
            err_msg = stderr if stderr else stdout
            log.warning(f"[ARENA] Server CRASH saat startup:\n{err_msg[:300]}")
            return False, err_msg
            
        log.info(f"[ARENA] Server berhasil berjalan (PID: {self.target_process.pid})")
        return True, "Server started successfully on port 5000."

    def start_third_party_server(self, target_dir: Path, start_command: list) -> tuple[bool, str]:
        """Menjalankan server web third-party rentan (misal DVPWA) di background."""
        self.stop_target_server() # Pastikan port bersih sebelum mulai
        
        log.info(f"[ARENA] Memulai target Third-Party di port {self.target_port}...")
        
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PORT": str(self.target_port)}
        try:
            self.target_process = subprocess.Popen(
                start_command,
                cwd=str(target_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(4) # Beri waktu server untuk booting
            
            if self.target_process.poll() is not None:
                stdout, stderr = self.target_process.communicate()
                err_msg = stderr if stderr else stdout
                log.warning(f"[ARENA] Third-Party Server CRASH saat startup:\n{err_msg[:300]}")
                return False, err_msg
                
            log.info(f"[ARENA] Third-Party Server berhasil berjalan (PID: {self.target_process.pid})")
            return True, "Third-party server started successfully."
        except Exception as e:
            return False, f"Exception starting third-party server: {str(e)}"


    def run_exploit(self, code: str, filename: str = "exploit.py", timeout: int = 15) -> dict:
        """Menjalankan script eksploit terhadap server yang sedang berjalan."""
        exploit_path = self.sandbox_dir / filename
        exploit_path.write_text(code, encoding="utf-8")
        
        log.info(f"[ARENA] Mengeksekusi script eksploit ({filename})...")
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        
        try:
            proc = subprocess.run(
                ["python", str(exploit_path)],
                cwd=str(self.sandbox_dir),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "status": "success" if proc.returncode == 0 else "error",
                "output": proc.stdout,
                "errors": proc.stderr,
                "returncode": proc.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "output": "", "errors": f"Exploit timeout setelah {timeout} detik"}
        except Exception as e:
            return {"status": "exception", "output": "", "errors": str(e)}

    def stop_target_server(self):
        """Mematikan server dan membersihkan port 5000."""
        if self.target_process:
            if self.target_process.poll() is None:
                log.info(f"[ARENA] Mematikan target server (PID: {self.target_process.pid})...")
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.target_process.pid)], capture_output=True)
                else:
                    self.target_process.kill()
            self.target_process = None
            
        # Cleanup agresif: Bunuh semua proses yang menduduki port 5000
        if os.name == 'nt':
            try:
                out = subprocess.check_output(f"netstat -ano | findstr :{self.target_port}", shell=True, text=True)
                for line in out.splitlines():
                    if "LISTENING" in line:
                        pid = line.strip().split()[-1]
                        if int(pid) > 0:
                            subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)
            except:
                pass
