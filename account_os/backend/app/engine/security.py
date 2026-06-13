from cryptography.fernet import Fernet
import os
import json
from typing import Dict, Any

# In production, this would be a persistent key from a secret manager
ENCRYPTION_KEY = os.getenv("MASTER_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    if os.getenv("ENV") == "production":
        raise ValueError("MASTER_ENCRYPTION_KEY must be set in production")
    print("⚠️ WARNING: MASTER_ENCRYPTION_KEY not set. Using ephemeral key for development.")
    ENCRYPTION_KEY = Fernet.generate_key().decode()

fernet = Fernet(ENCRYPTION_KEY.encode())

class EncryptionService:
    """
    Handles encryption and decryption of sensitive data like OAuth tokens.
    """
    @staticmethod
    def encrypt_data(data: Dict[str, Any]) -> str:
        json_str = json.dumps(data)
        return fernet.encrypt(json_str.encode()).decode()

    @staticmethod
    def decrypt_data(encrypted_str: str) -> Dict[str, Any]:
        decrypted_bytes = fernet.decrypt(encrypted_str.encode())
        return json.loads(decrypted_bytes.decode())
