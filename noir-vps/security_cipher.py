import os
import base64
import json
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

log = logging.getLogger("SecurityCipher")

class SecurityCipher:
    """
    AES-256 (Fernet) Encryption layer untuk komunikasi Noir Sovereign v30.
    Menggunakan deterministik KDF dari Master API Key untuk menghasilkan kunci enkripsi
    agar VPS dan Android memiliki kunci symetric yang sama tanpa hardcode key.
    """
    def __init__(self):
        # Gunakan API Key yang ada sebagai "password" dasar
        self.master_key = os.environ.get("NOIR_API_KEY", "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026")
        self.salt = b'noir_sovereign_v30_salt_aegis'  # Static salt untuk sinkronisasi
        self.fernet = self._derive_key()

    def _derive_key(self) -> Fernet:
        """Menghasilkan kunci Fernet AES-256 yang aman dari master_key dan salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)

    def encrypt_payload(self, data: dict) -> str:
        """Mengenkripsi dictionary JSON menjadi string tersandi."""
        try:
            json_data = json.dumps(data).encode('utf-8')
            encrypted_data = self.fernet.encrypt(json_data)
            return encrypted_data.decode('utf-8')
        except Exception as e:
            log.error(f"[CIPHER] Encryption failed: {e}")
            raise

    def decrypt_payload(self, encrypted_str: str) -> dict:
        """Mendekripsi string tersandi menjadi dictionary JSON."""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_str.encode('utf-8'))
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            log.error(f"[CIPHER] Decryption failed: {e}")
            raise

# Singleton instance
aegis_cipher = SecurityCipher()
