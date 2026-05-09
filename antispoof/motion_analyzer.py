"""Head movement tracking for liveness detection"""

import numpy as np
from collections import deque


class MotionAnalyzer:
    """Analyzes head motion for liveness detection"""
    
    def __init__(self, history_length=30):
        self.position_history = deque(maxlen=history_length)
        self.motion_threshold = 0.02  # Minimum motion to consider "live"
        
    def analyze(self, face_data) -> bool:
        """
        Analyze head motion from face landmarks
        Returns True if natural motion detected
        """
        # Get nose tip position (good indicator of head movement)
        landmarks = face_data.landmarks
        
        if 'nose_tip' not in landmarks:
            return False
            
        nose_pos = np.array(landmarks['nose_tip'][0])
        self.position_history.append(nose_pos)
        
        if len(self.position_history) < 5:
            return False
            
        # Calculate motion variance
        positions = np.array(self.position_history)
        variance = np.var(positions, axis=0)
        total_variance = np.sum(variance)
        
        # Natural heads have some motion
        # Completely static faces are suspicious (photo/video)
        return total_variance > self.motion_threshold