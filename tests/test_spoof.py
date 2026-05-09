"""Test anti-spoofing functionality"""

import unittest
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from antispoof.blink_detector import BlinkDetector
from antispoof.motion_analyzer import MotionAnalyzer


class TestAntiSpoofing(unittest.TestCase):
    
    def setUp(self):
        self.blink_detector = BlinkDetector()
        self.motion_analyzer = MotionAnalyzer()
        
    def test_blink_detector_initialization(self):
        """Test blink detector initialization"""
        self.assertIsNotNone(self.blink_detector)
        self.assertEqual(self.blink_detector.blink_counter, 0)
        
    def test_motion_analyzer_initialization(self):
        """Test motion analyzer initialization"""
        self.assertIsNotNone(self.motion_analyzer)
        self.assertEqual(len(self.motion_analyzer.position_history), 0)
        
    def test_eye_aspect_ratio(self):
        """Test EAR calculation"""
        # Mock eye points
        eye_points = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
        ear = self.blink_detector.eye_aspect_ratio(eye_points)
        self.assertGreaterEqual(ear, 0)


if __name__ == '__main__':
    unittest.main()