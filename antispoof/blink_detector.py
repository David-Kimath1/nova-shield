"""Eye blink detection for liveness verification"""

import cv2
import numpy as np
from scipy.spatial import distance as dist


class BlinkDetector:
    """Detects eye blinks to verify liveness"""
    
    def __init__(self):
        # Eye aspect ratio thresholds
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 2
        
        self.blink_counter = 0
        self.total_blinks = 0
        
    def eye_aspect_ratio(self, eye_points):
        """Calculate eye aspect ratio"""
        # Compute Euclidean distances
        A = dist.euclidean(eye_points[1], eye_points[5])
        B = dist.euclidean(eye_points[2], eye_points[4])
        C = dist.euclidean(eye_points[0], eye_points[3])
        
        ear = (A + B) / (2.0 * C)
        return ear
        
    def detect(self, face_data) -> bool:
        """
        Detect if face shows signs of life (blinking)
        Returns True if liveness detected
        """
        landmarks = face_data.landmarks
        
        # Check if eye landmarks exist
        if 'left_eye' not in landmarks or 'right_eye' not in landmarks:
            return False
            
        # Calculate eye aspect ratios
        left_ear = self.eye_aspect_ratio(landmarks['left_eye'])
        right_ear = self.eye_aspect_ratio(landmarks['right_eye'])
        ear = (left_ear + right_ear) / 2.0
        
        # Check for blink
        if ear < self.EYE_AR_THRESH:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.EYE_AR_CONSEC_FRAMES:
                self.total_blinks += 1
            self.blink_counter = 0
            
        # Liveness requires at least 1 blink in recent history
        # For continuous verification, we check recent activity
        return self.total_blinks > 0 or self.blink_counter > 0