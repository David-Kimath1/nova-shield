"""Detects unusual behavior patterns"""

import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import deque


class AnomalyDetector:
    """Detects anomalies in real-time behavior"""
    
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
        self.anomaly_threshold = 2.5  # Standard deviations
        
    def add_observation(self, value: float):
        """Add new observation to history"""
        self.history.append(value)
        
    def detect(self, value: float) -> Dict[str, Any]:
        """
        Detect if value is anomalous based on history
        """
        if len(self.history) < 10:
            return {'is_anomaly': False, 'score': 0.0}
            
        mean = np.mean(self.history)
        std = np.std(self.history)
        
        if std < 1e-6:
            z_score = 0
        else:
            z_score = abs(value - mean) / std
            
        is_anomaly = z_score > self.anomaly_threshold
        anomaly_score = min(z_score / self.anomaly_threshold, 1.0)
        
        return {
            'is_anomaly': is_anomaly,
            'score': anomaly_score,
            'z_score': z_score,
            'expected': float(mean)
        }
        
    def detect_sequence(self, values: list) -> float:
        """Detect anomalies in a sequence of values"""
        if len(values) < 3:
            return 0.0
            
        # Calculate rate of change
        diffs = np.diff(values)
        avg_change = np.mean(np.abs(diffs))
        max_change = np.max(np.abs(diffs))
        
        # Unusual rapid changes are suspicious
        if avg_change > 0:
            change_ratio = max_change / avg_change
            return min(change_ratio / 5, 1.0)
            
        return 0.0