"""Event bus for inter-component communication"""

import asyncio
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """System event types"""
    FACE_DETECTED = "face_detected"
    FACE_RECOGNIZED = "face_recognized"
    FACE_UNKNOWN = "face_unknown"
    INTRUDER_DETECTED = "intruder_detected"
    SPOOF_ATTEMPT = "spoof_attempt"
    SYSTEM_LOCK = "system_lock"
    SYSTEM_UNLOCK = "system_unlock"
    ALERT_TRIGGERED = "alert_triggered"
    BEHAVIOR_ANOMALY = "behavior_anomaly"


@dataclass
class Event:
    """Event data structure"""
    type: EventType
    data: Any
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventBus:
    """Central event bus for pub/sub communication"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._async_queue = asyncio.Queue()
        self._running = False
        
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
            
    async def emit(self, event: Event):
        """Emit an event synchronously"""
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
                    
    async def emit_async(self, event: Event):
        """Emit event asynchronously via queue"""
        await self._async_queue.put(event)
        
    async def start(self):
        """Start event processing loop"""
        self._running = True
        while self._running:
            try:
                event = await self._async_queue.get()
                await self.emit(event)
            except asyncio.CancelledError:
                break
                
    def stop(self):
        """Stop event processing"""
        self._running = False