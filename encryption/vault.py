"""Encrypted storage for biometric data"""

import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from base64 import b64encode, b64decode
from pathlib import Path
from app.logger import get_logger


class Vault:
    """Secure encrypted storage for sensitive data"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.key_path = config.storage_path / "encrypted" / ".vault_key"
        self.cipher = None
        self._init_cipher()
        
    def _init_cipher(self):
        """Initialize encryption cipher"""
        if self.key_path.exists():
            # Load existing key
            key = self.key_path.read_bytes()
        else:
            # Generate new key
            key = Fernet.generate_key()
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            self.key_path.write_bytes(key)
            os.chmod(self.key_path, 0o600)  # Secure permissions
            
        self.cipher = Fernet(key)
        
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data"""
        if self.cipher:
            return self.cipher.encrypt(data)
        raise Exception("[VAULT] Cipher not initialized")
        
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data"""
        if self.cipher:
            return self.cipher.decrypt(encrypted_data)
        raise Exception("[VAULT] Cipher not initialized")
        
    def encrypt_string(self, text: str) -> str:
        """Encrypt string and return base64"""
        encrypted = self.encrypt(text.encode())
        return b64encode(encrypted).decode()
        
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt base64 string"""
        encrypted = b64decode(encrypted_text)
        return self.decrypt(encrypted).decode()
        
    def store_face_data(self, user_id: str, face_encoding: list) -> bool:
        """Store encrypted face encoding"""
        try:
            data = {
                'user_id': user_id,
                'encoding': face_encoding,
                'created': str(datetime.now())
            }
            
            json_data = json.dumps(data).encode()
            encrypted = self.encrypt(json_data)
            
            storage_file = self.config.storage_path / "encrypted" / f"{user_id}.enc"
            storage_file.write_bytes(encrypted)
            
            return True
            
        except Exception as e:
            self.logger.error(f"[VAULT] Failed to store face data: {e}")
            return False