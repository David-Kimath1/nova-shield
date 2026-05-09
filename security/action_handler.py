"""Handles security actions (lock, alert, allow)"""

import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from app.logger import get_logger
from app.event_bus import EventBus, Event, EventType
from security.intrusion_logger import IntrusionLogger
from security.lock_controller import LockController


class ActionHandler:
    """Executes security actions"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = get_logger(__name__)
        self.lock_controller = LockController()
        self.intrusion_logger = IntrusionLogger(config)
        
    async def allow_access(self, face_data):
        """Allow access (unlock system)"""
        self.logger.info("[ACCESS] Access granted")
        
        # Unlock the system
        self.lock_controller.unlock()
        
        # Log successful access
        self.intrusion_logger.log_access(
            status="ALLOWED",
            face_data=face_data
        )
        
        # Emit event
        await self.event_bus.emit_async(Event(
            EventType.SYSTEM_UNLOCK,
            {"face": face_data, "status": "allowed"}
        ))
        
    async def alert(self, face_data, risk_score: float):
        """Trigger alert for suspicious activity"""
        self.logger.warning(f"[ALERT] Suspicious activity detected (risk: {risk_score:.2f})")
        
        # Log intrusion attempt
        snapshot_path = self.intrusion_logger.log_intrusion(
            face_data=face_data,
            risk_score=risk_score,
            action="ALERT"
        )
        
        # Emit alert event
        await self.event_bus.emit_async(Event(
            EventType.ALERT_TRIGGERED,
            {
                "face": face_data,
                "risk": risk_score,
                "snapshot": snapshot_path
            }
        ))
        
    async def lock_system(self):
        """Lock the system immediately"""
        self.logger.warning("[LOCK] System locked due to security threat")
        
        # Lock the system
        self.lock_controller.lock()
        
        # Log lock event
        self.intrusion_logger.log_system_lock()
        
        # Emit lock event
        await self.event_bus.emit_async(Event(
            EventType.SYSTEM_LOCK,
            {"timestamp": datetime.now()}
        ))