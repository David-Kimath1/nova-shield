"""Face encoding for registered users"""

import face_recognition
import pickle
import numpy as np
from pathlib import Path
from encryption.vault import Vault
from app.logger import get_logger


class FaceEncoder:
    """Encodes and stores face data securely"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.vault = Vault(config)
        self.encodings_path = config.storage_path / "encrypted" / "face_encodings.enc"
        
    def encode_from_image(self, image_path: str) -> np.ndarray:
        """Extract face encoding from image"""
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if not encodings:
            self.logger.error("[FAIL] No face found in image")
            return None
            
        return encodings[0]
        
    def encode_from_frame(self, frame, face_location) -> np.ndarray:
        """Extract face encoding from camera frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_frame, [face_location])
        
        if encodings:
            return encodings[0]
        return None
        
    def register_face(self, name: str, encoding: np.ndarray) -> bool:
        """Register a new face encoding securely"""
        try:
            # Load existing encodings
            encodings = self._load_encodings()
            
            # Add new encoding
            encodings[name] = {
                'encoding': encoding.tolist(),
                'registered_at': str(datetime.now())
            }
            
            # Save encrypted
            self._save_encodings(encodings)
            self.logger.info(f"[OK] Face registered for {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"[FAIL] Failed to register face: {e}")
            return False
            
    def _load_encodings(self) -> dict:
        """Load encrypted face encodings"""
        if not self.encodings_path.exists():
            return {}
            
        encrypted_data = self.encodings_path.read_bytes()
        decrypted = self.vault.decrypt(encrypted_data)
        return pickle.loads(decrypted)
        
    def _save_encodings(self, encodings: dict):
        """Save encrypted face encodings"""
        data = pickle.dumps(encodings)
        encrypted = self.vault.encrypt(data)
        self.encodings_path.parent.mkdir(parents=True, exist_ok=True)
        self.encodings_path.write_bytes(encrypted)