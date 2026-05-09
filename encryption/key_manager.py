"""Manages encryption keys securely"""

import os
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode


class KeyManager:
    """Manages encryption keys with user authentication"""
    
    def __init__(self, key_file_path):
        self.key_file_path = key_file_path
        
    def derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = b64encode(kdf.derive(password.encode()))
        return key
        
    def create_key(self, password: str = None):
        """Create a new encryption key"""
        if not password:
            password = getpass.getpass("Enter encryption password: ")
            confirm = getpass.getpass("Confirm password: ")
            
            if password != confirm:
                raise Exception("[KEY] Passwords do not match")
                
        salt = os.urandom(16)
        key = self.derive_key_from_password(password, salt)
        
        # Store salt and key hint (not the actual key)
        key_data = {
            'salt': b64encode(salt).decode(),
            'key_hint': b64encode(key[:16]).decode()
        }
        
        with open(self.key_file_path, 'w') as f:
            json.dump(key_data, f)
            
        os.chmod(self.key_file_path, 0o600)
        
        return Fernet(key)
        
    def load_key(self, password: str = None) -> Fernet:
        """Load encryption key with password"""
        if not self.key_file_path.exists():
            return self.create_key(password)
            
        with open(self.key_file_path, 'r') as f:
            key_data = json.load(f)
            
        if not password:
            password = getpass.getpass("Enter encryption password: ")
            
        salt = b64decode(key_data['salt'])
        key = self.derive_key_from_password(password, salt)
        
        # Verify key by checking hint
        expected_hint = key_data['key_hint']
        actual_hint = b64encode(key[:16]).decode()
        
        if expected_hint != actual_hint:
            raise Exception("[KEY] Invalid password")
            
        return Fernet(key)