import os
import json
import logging
import requests
from typing import Dict, Any, Optional

log = logging.getLogger("CloudMemory")

class CloudMemoryClient:
    """
    Penghubung antara Local PC dan VPS Alibaba (Cloud Storage).
    Bertugas memindahkan proses I/O penyimpanan ke server eksternal,
    meringankan storage dan komputasi lokal.
    """
    
    # Endpoint VPS Alibaba sesuai arsitektur sebelumnya
    VPS_HOST = "http://8.215.23.17"
    API_STATE_ENDPOINT = f"{VPS_HOST}/api/state"
    API_MEMORY_ENDPOINT = f"{VPS_HOST}/api/memory"
    
    TIMEOUT = 5.0 # Detik

    @classmethod
    def ping_server(cls) -> bool:
        """Cek apakah VPS menyala dan API terhubung."""
        try:
            res = requests.get(cls.API_STATE_ENDPOINT, timeout=cls.TIMEOUT)
            return res.status_code == 200
        except requests.exceptions.RequestException as e:
            log.warning(f"[CloudMemory] Gagal terhubung ke VPS: {e}")
            return False

    @classmethod
    def pull_knowledge(cls, key: str) -> Optional[Dict[str, Any]]:
        """Mengambil data (ingatan) dari VPS."""
        try:
            res = requests.get(f"{cls.API_MEMORY_ENDPOINT}/{key}", timeout=cls.TIMEOUT)
            if res.status_code == 200:
                log.info(f"[CloudMemory] Berhasil mengunduh ingatan '{key}' dari VPS.")
                return res.json()
            else:
                log.warning(f"[CloudMemory] Ingatan '{key}' tidak ditemukan di VPS. (Status {res.status_code})")
                return None
        except requests.exceptions.RequestException as e:
            log.error(f"[CloudMemory] API Error saat pull: {e}")
            return None

    @classmethod
    def push_knowledge(cls, key: str, payload: Dict[str, Any]) -> bool:
        """Mengirim data (ingatan baru) untuk disimpan di VPS secara permanen."""
        try:
            res = requests.post(
                f"{cls.API_MEMORY_ENDPOINT}/{key}", 
                json=payload, 
                timeout=cls.TIMEOUT
            )
            if res.status_code in [200, 201]:
                log.info(f"[CloudMemory] Berhasil mengunggah ingatan '{key}' ke VPS Alibaba.")
                return True
            else:
                log.error(f"[CloudMemory] Gagal mengunggah. (Status {res.status_code}) - {res.text}")
                return False
        except requests.exceptions.RequestException as e:
            log.error(f"[CloudMemory] API Error saat push: {e}")
            return False

    @classmethod
    def offload_task(cls, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Melempar eksekusi tugas berat (seperti Fuzzing atau Attack Generation) 
        agar CPU VPS yang mengerjakannya, lalu mengembalikan hasilnya ke PC lokal.
        """
        try:
            log.info(f"[CloudMemory] Offloading tugas komputasi berat '{task_type}' ke CPU VPS...")
            res = requests.post(
                f"{cls.VPS_HOST}/api/compute/{task_type}",
                json=payload,
                timeout=30.0 # Timeout lebih lama untuk komputasi
            )
            if res.status_code == 200:
                return res.json()
            return {"error": f"VPS Compute Failed: Status {res.status_code}"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test sederhana saat dieksekusi langsung
    logging.basicConfig(level=logging.INFO)
    print("=== Menguji Konektivitas Noir Cloud Memory ===")
    status = CloudMemoryClient.ping_server()
    print(f"Status VPS Alibaba (8.215.23.17): {'ONLINE' if status else 'OFFLINE/UNREACHABLE'}")
