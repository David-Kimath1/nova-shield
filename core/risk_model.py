"""Threat scoring system for security evaluation"""

import numpy as np
from typing import Dict, Any, Optional


class RiskModel:
    """Calculates threat risk scores"""
    
    def __init__(self, config):
        self.config = config
        
        # Weights for different factors
        self.weights = {
            'face_match': 0.35,
            'liveness': 0.30,
            'motion': 0.20,
            'behavior': 0.15
        }
        
    def calculate(self, 
                  face_match: Optional[Dict],
                  is_live: bool,
                  has_motion: bool,
                  behavior_score: float = 1.0) -> float:
        """
        Calculate overall risk score (0 = safe, 1 = high risk)
        """
        risk = 0.0
        
        # Face match score (if no match, high risk)
        if face_match is None or not face_match.get('matched', False):
            risk += self.weights['face_match'] * 1.0
        else:
            distance = face_match.get('distance', 1.0)
            risk += self.weights['face_match'] * min(distance, 1.0)
            
        # Liveness score
        if not is_live:
            risk += self.weights['liveness'] * 1.0
            
        # Motion score
        if not has_motion:
            risk += self.weights['motion'] * 0.5  # Still face is suspicious
            
        # Behavior score
        risk += self.weights['behavior'] * (1 - behavior_score)
        
        return min(risk, 1.0)
        
    def get_risk_level(self, risk_score: float) -> str:
        """Get risk level string"""
        if risk_score < 0.2:
            return "LOW"
        elif risk_score < 0.6:
            return "MEDIUM"
        else:
            return "HIGH"