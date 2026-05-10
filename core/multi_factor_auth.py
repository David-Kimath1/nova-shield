"""Multi-Factor Authentication Fusion Engine"""

import numpy as np
from collections import deque
import time
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class FactorScore:
    name: str
    score: float
    weight: float
    details: str

class MultiFactorAuthenticator:
    """Combines multiple authentication factors"""
    
    def __init__(self):
        self.typing_patterns = deque(maxlen=50)
        self.mouse_movements = deque(maxlen=100)
        self.voice_samples = []
        
        # Factor weights
        self.weights = {
            'face': 0.35,
            'typing': 0.20,
            'voice': 0.20,
            'behavior': 0.15,
            'device': 0.10
        }
        
        # Thresholds
        self.trust_threshold = 0.75
        self.warn_threshold = 0.50
        
    def analyze_typing_pattern(self, key_timings: list) -> float:
        if len(key_timings) < 5:
            return 0.5
            
        intervals = np.diff(key_timings)
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        self.typing_patterns.append({
            'mean': mean_interval,
            'std': std_interval,
            'timestamp': time.time()
        })
        
        if len(self.typing_patterns) > 10:
            historical_mean = np.mean([p['mean'] for p in self.typing_patterns])
            historical_std = np.mean([p['std'] for p in self.typing_patterns])
            
            mean_diff = abs(mean_interval - historical_mean) / historical_mean
            std_diff = abs(std_interval - historical_std) / historical_std
            
            confidence = 1 - min((mean_diff + std_diff) / 2, 1)
            return confidence
            
        return 0.5
        
    def analyze_mouse_behavior(self, movements: list) -> float:
        if len(movements) < 10:
            return 0.5
            
        velocities = []
        
        for i in range(1, len(movements)):
            dx = movements[i][0] - movements[i-1][0]
            dy = movements[i][1] - movements[i-1][1]
            dt = movements[i][2] - movements[i-1][2]
            
            if dt > 0:
                velocity = np.sqrt(dx**2 + dy**2) / dt
                velocities.append(velocity)
                
        velocity_variance = np.var(velocities) if velocities else 0
        
        if 10 < velocity_variance < 1000:
            return 0.8
        elif velocity_variance < 10:
            return 0.3
        else:
            return 0.6
            
    def verify_voice(self, voice_embedding):
        # Placeholder for voice verification
        return 0.85
        
    def compute_trust_score(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        scores = []
        
        if 'face_match' in factors:
            face_score = factors['face_match'].get('confidence', 0)
            scores.append(FactorScore('Face', face_score, self.weights['face'], 
                                     f"Match confidence: {face_score:.2%}"))
        
        if 'typing_timings' in factors:
            typing_score = self.analyze_typing_pattern(factors['typing_timings'])
            scores.append(FactorScore('Typing', typing_score, self.weights['typing'],
                                     f"Typing rhythm: {typing_score:.2%}"))
        
        if 'voice_embedding' in factors:
            voice_score = self.verify_voice(factors['voice_embedding'])
            scores.append(FactorScore('Voice', voice_score, self.weights['voice'],
                                     f"Voice match: {voice_score:.2%}"))
        
        if 'mouse_movements' in factors:
            behavior_score = self.analyze_mouse_behavior(factors['mouse_movements'])
            scores.append(FactorScore('Behavior', behavior_score, self.weights['behavior'],
                                     f"Behavior pattern: {behavior_score:.2%}"))
        
        total_weight = sum(f.weight for f in scores)
        if total_weight > 0:
            final_score = sum(f.score * f.weight for f in scores) / total_weight
        else:
            final_score = 0
            
        if final_score >= self.trust_threshold:
            trust_level = "TRUSTED"
            action = "ALLOW"
        elif final_score >= self.warn_threshold:
            trust_level = "SUSPICIOUS"
            action = "VERIFY_MORE"
        else:
            trust_level = "HIGH_RISK"
            action = "LOCK"
            
        return {
            'final_score': final_score,
            'trust_level': trust_level,
            'action': action,
            'factors': [{'name': f.name, 'score': f.score, 'details': f.details} 
                       for f in scores]
        }

if __name__ == "__main__":
    mfa = MultiFactorAuthenticator()
    result = mfa.compute_trust_score({
        'face_match': {'confidence': 0.92},
        'typing_timings': [0.1, 0.15, 0.12, 0.14, 0.11, 0.13],
        'mouse_movements': [(100,200,0.1), (105,205,0.2), (110,210,0.3)]
    })
    
    print(f"Final Trust Score: {result['final_score']:.2%}")
    print(f"Trust Level: {result['trust_level']}")
    print(f"Action: {result['action']}")
    for factor in result['factors']:
        print(f"  - {factor['name']}: {factor['score']:.2%} ({factor['details']})")
