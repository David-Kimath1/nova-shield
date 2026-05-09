"""Test face recognition functionality"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from recognition.face_encoder import FaceEncoder
from recognition.face_matcher import FaceMatcher
from app.config import Config


class TestFaceRecognition(unittest.TestCase):
    
    def setUp(self):
        self.config = Config()
        self.encoder = FaceEncoder(self.config)
        self.matcher = FaceMatcher(self.config)
        
    def test_face_encoding(self):
        """Test face encoding extraction"""
        # This test requires a test image
        # test_image = "test_face.jpg"
        # encoding = self.encoder.encode_from_image(test_image)
        # self.assertIsNotNone(encoding)
        pass
        
    def test_face_matching(self):
        """Test face matching logic"""
        # Create test encodings
        import numpy as np
        test_encoding = np.random.rand(128)
        
        # Should return None when no registered faces
        result = self.matcher.match(test_encoding)
        self.assertIsNone(result)
        
    def test_threshold_config(self):
        """Test threshold configuration"""
        self.assertGreater(self.config.recognition_threshold, 0)
        self.assertLess(self.config.recognition_threshold, 1)


if __name__ == '__main__':
    unittest.main()