"""Threat Level Management"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

class ThreatLevel(Enum):
    GREEN = "GREEN"      # Trusted user
    YELLOW = "YELLOW"    # Suspicious behavior
    ORANGE = "ORANGE"    # Possible spoof attempt
    RED = "RED"          # Intruder detected
    
@dataclass
class ThreatEvent:
    level: ThreatLevel
    reason: str
    timestamp: datetime
    actions_taken: List[str]

class ThreatEngine:
    """Manages threat levels and triggers responses"""
    
    def __init__(self):
        self.current_level = ThreatLevel.GREEN
        self.event_history: List[ThreatEvent] = []
        self.threat_score = 0  # 0-100
        
        # Triggers and their threat scores
        self.triggers = {
            'unknown_face': 40,
            'spoof_attempt': 70,
            'multiple_faces': 50,
            'unusual_hour': 20,
            'failed_auth': 30,
            'rapid_movement': 25,
            'no_face_detected': 15,
            'camera_obstructed': 35
        }
        
    def update_threat(self, events: dict) -> ThreatLevel:
        """Update threat level based on events"""
        self.threat_score = 0
        
        for event, triggered in events.items():
            if triggered and event in self.triggers:
                self.threat_score += self.triggers[event]
                
        # Cap at 100
        self.threat_score = min(self.threat_score, 100)
        
        # Determine new level
        if self.threat_score < 20:
            new_level = ThreatLevel.GREEN
        elif self.threat_score < 50:
            new_level = ThreatLevel.YELLOW
        elif self.threat_score < 75:
            new_level = ThreatLevel.ORANGE
        else:
            new_level = ThreatLevel.RED
            
        # Log level change
        if new_level != self.current_level:
            self._log_threat_change(new_level)
            
        self.current_level = new_level
        return new_level
        
    def _log_threat_change(self, new_level: ThreatLevel):
        """Log threat level change"""
        actions = self._get_actions_for_level(new_level)
        
        event = ThreatEvent(
            level=new_level,
            reason=f"Threat score reached {self.threat_score}",
            timestamp=datetime.now(),
            actions_taken=actions
        )
        self.event_history.append(event)
        
        # Execute actions
        self._execute_actions(actions)
        
    def _get_actions_for_level(self, level: ThreatLevel) -> List[str]:
        """Get actions for threat level"""
        actions = {
            ThreatLevel.GREEN: ["Continue monitoring"],
            ThreatLevel.YELLOW: ["Log event", "Increase monitoring"],
            ThreatLevel.ORANGE: ["Capture snapshot", "Send warning", "Verify liveness"],
            ThreatLevel.RED: ["Lock system", "Send alert", "Save intruder image", "Notify admin"]
        }
        return actions.get(level, ["Log event"])
        
    def _execute_actions(self, actions: List[str]):
        """Execute threat response actions"""
        for action in actions:
            print(f"[THREAT] Executing: {action}")
            # Implement actual actions here
            
    def get_status(self) -> dict:
        """Get current threat status"""
        return {
            'level': self.current_level.value,
            'score': self.threat_score,
            'history_count': len(self.event_history),
            'last_event': self.event_history[-1] if self.event_history else None
        }
