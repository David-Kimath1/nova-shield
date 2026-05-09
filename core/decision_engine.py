"""Decision engine for security actions"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class SecurityDecision:
    """Security decision result"""
    action: str  # ALLOW, ALERT, LOCK
    confidence: float
    reason: str


class DecisionEngine:
    """Makes final security decisions based on risk assessment"""
    
    def __init__(self, config, risk_model):
        self.config = config
        self.risk_model = risk_model
        
        # Decision thresholds
        self.allow_threshold = 0.2    # Risk below 0.2 = allow
        self.alert_threshold = 0.6    # Risk 0.2-0.6 = alert
        # Risk above 0.6 = lock
        
    def decide(self, risk_score: float) -> str:
        """Make decision based on risk score"""
        if risk_score < self.allow_threshold:
            return "ALLOW"
        elif risk_score < self.alert_threshold:
            return "ALERT"
        else:
            return "LOCK"
            
    def decide_with_context(self, risk_score: float, context: Dict[str, Any]) -> SecurityDecision:
        """Make decision with additional context"""
        
        # Check for unusual hour
        from datetime import datetime
        current_hour = datetime.now().hour
        
        if current_hour < 6 or current_hour > 22:
            risk_score *= 1.3  # Increase risk for night access
            
        # Check for multiple recent attempts
        if context.get('recent_failures', 0) > 3:
            risk_score *= 1.5
            
        if risk_score < self.allow_threshold:
            return SecurityDecision("ALLOW", 1 - risk_score, "Low risk - access granted")
        elif risk_score < self.alert_threshold:
            return SecurityDecision("ALERT", risk_score, "Medium risk - logging and monitoring")
        else:
            return SecurityDecision("LOCK", risk_score, "High risk - system locked")