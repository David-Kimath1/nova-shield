"""Face matching and comparison"""

import face_recognition
import numpy as np
from typing import Dict, Optional
from recognition.face_encoder import FaceEncoder
from app.logger import get_logger


class FaceMatcher:
    """Matches detected faces against registered users"""
    
    def __init__(self, config, device: str = "cpu"):
        self.config = config
        self.device = device
        self.logger = get_logger(__name__)
        self.encoder = FaceEncoder(config)
        self.registered_faces = {}
        self.threshold = config.recognition_threshold
        
        self._load_registered_faces()
        
    def _load_registered_faces(self):
        """Load all registered face encodings"""
        encodings = self.encoder._load_encodings()
        
        for name, data in encodings.items():
            self.registered_faces[name] = np.array(data['encoding'])
            
        self.logger.info(f"[FACE] Loaded {len(self.registered_faces)} registered faces")
        
    def match(self, face_encoding: np.ndarray) -> Optional[Dict]:
        """
        Match face encoding against registered users
        Returns dict with match info or None if no match
        """
        if not self.registered_faces:
            return None
            
        # Compare with all registered faces
        names = list(self.registered_faces.keys())
        encodings = list(self.registered_faces.values())
        
        distances = face_recognition.face_distance(encodings, face_encoding)
        best_match_idx = np.argmin(distances)
        best_distance = distances[best_match_idx]
        
        if best_distance < self.threshold:
            return {
                'matched': True,
                'name': names[best_match_idx],
                'distance': float(best_distance),
                'confidence': 1 - best_distance
            }
        else:
            return {
                'matched': False,
                'distance': float(best_distance),
                'confidence': 1 - best_distance
            }
            
    def verify(self, face_encoding: np.ndarray, expected_name: str) -> bool:
        """Verify if face matches expected user"""
        if expected_name not in self.registered_faces:
            return False
            
        expected_encoding = self.registered_faces[expected_name]
        distance = face_recognition.face_distance([expected_encoding], face_encoding)[0]
        
        return distance < self.threshold