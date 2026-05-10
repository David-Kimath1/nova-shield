"""Continuous Session Verification"""

import time
from collections import deque
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class SessionState:
    face_present: bool
    confidence: float
    last_verified: float
    verification_count: int

class ContinuousVerifier:
    """Verifies identity throughout the session"""
    
    def __init__(self, interval_seconds=5, confidence_threshold=0.7):
        self.interval = interval_seconds
        self.confidence_threshold = confidence_threshold
        self.session_state: Optional[SessionState] = None
        self.confidence_history = deque(maxlen=20)
        self.last_check = time.time()
        self.warning_issued = False
        
    def verify(self, face_confidence: float, face_detected: bool) -> dict:
        """Verify user continuously"""
        current_time = time.time()
        
        # Initialize session
        if self.session_state is None:
            self.session_state = SessionState(
                face_present=face_detected,
                confidence=face_confidence,
                last_verified=current_time,
                verification_count=1
            )
            return {'trusted': True, 'reason': 'Session started'}
            
        # Time for re-verification
        if current_time - self.last_check >= self.interval:
            self.last_check = current_time
            
            # Track confidence over time
            self.confidence_history.append(face_confidence)
            
            # Check if face disappeared
            if not face_detected:
                return {
                    'trusted': False,
                    'reason': 'Face no longer detected',
                    'action': 'lock'
                }
                
            # Check confidence drop
            if len(self.confidence_history) > 5:
                avg_confidence = np.mean(self.confidence_history)
                if avg_confidence < self.confidence_threshold:
                    if not self.warning_issued:
                        self.warning_issued = True
                        return {
                            'trusted': False,
                            'reason': f'Confidence dropped to {avg_confidence:.2%}',
                            'action': 'warn'
                        }
                    else:
                        return {
                            'trusted': False,
                            'reason': 'Persistent low confidence',
                            'action': 'lock'
                        }
                        
            # Update session
            self.session_state.face_present = face_detected
            self.session_state.confidence = face_confidence
            self.session_state.last_verified = current_time
            self.session_state.verification_count += 1
            self.warning_issued = False
            
            return {'trusted': True, 'reason': 'Continuous verification passed'}
            
        return {'trusted': True, 'reason': 'Within verification window'}
        
    def get_session_stats(self) -> dict:
        """Get session statistics"""
        if self.session_state:
            return {
                'duration': time.time() - self.session_state.last_verified,
                'verifications': self.session_state.verification_count,
                'avg_confidence': np.mean(self.confidence_history) if self.confidence_history else 0,
                'status': 'active' if self.session_state.face_present else 'no_face'
            }
        return {'status': 'no_session'}
