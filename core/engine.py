"""Main security engine - coordinates all components"""

import asyncio
from typing import Optional
import cv2

from app.logger import get_logger
from app.event_bus import EventBus, Event, EventType
from core.decision_engine import DecisionEngine
from core.risk_model import RiskModel
from vision.camera_stream import CameraStream
from vision.frame_processor import FrameProcessor
from recognition.face_matcher import FaceMatcher
from antispoof.blink_detector import BlinkDetector
from antispoof.motion_analyzer import MotionAnalyzer
from ai.behavior_model import BehaviorModel
from security.action_handler import ActionHandler
from notifications.alert_router import AlertRouter


class SecurityEngine:
    """Main security coordination engine"""
    
    def __init__(self, config, event_bus: EventBus, device: str):
        self.config = config
        self.event_bus = event_bus
        self.device = device
        self.logger = get_logger(__name__)
        
        # Initialize components
        self.camera = None
        self.frame_processor = None
        self.face_matcher = None
        self.blink_detector = None
        self.motion_analyzer = None
        self.behavior_model = None
        self.decision_engine = None
        self.risk_model = None
        self.action_handler = None
        self.alert_router = None
        
        self.running = False
        self.current_face = None
        self.consecutive_unknown = 0
        
    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Vision components
            self.camera = CameraStream(self.config)
            self.frame_processor = FrameProcessor(self.config, self.device)
            
            # Recognition components
            self.face_matcher = FaceMatcher(self.config, self.device)
            
            # Anti-spoofing
            self.blink_detector = BlinkDetector()
            self.motion_analyzer = MotionAnalyzer()
            
            # AI components
            if self.config.behavior_learning_enabled:
                self.behavior_model = BehaviorModel(self.config)
                
            # Decision components
            self.risk_model = RiskModel(self.config)
            self.decision_engine = DecisionEngine(self.config, self.risk_model)
            
            # Action components
            self.action_handler = ActionHandler(self.config, self.event_bus)
            self.alert_router = AlertRouter(self.config, self.event_bus)
            
            # Start camera
            if not await self.camera.start():
                self.logger.error("[FAIL] Failed to start camera")
                return False
                
            # Load face database
            if not self.face_matcher.load_encodings():
                self.logger.warning("[WARN] No face encodings found. Please register a face.")
                
            # Start event bus
            asyncio.create_task(self.event_bus.start())
            
            self.running = True
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Initialization failed: {e}")
            return False
            
    async def process_frame(self):
        """Process single frame from camera"""
        if not self.running:
            return
            
        # Get frame from camera
        frame = await self.camera.read()
        if frame is None:
            return
            
        # Process frame (detect faces)
        processed = self.frame_processor.process(frame)
        
        if processed.has_faces:
            for face_data in processed.faces:
                # Run face recognition
                match = self.face_matcher.match(face_data.encoding)
                
                # Run anti-spoofing
                is_live = self.blink_detector.detect(face_data)
                has_motion = self.motion_analyzer.analyze(face_data)
                
                # Calculate risk score
                risk = self.risk_model.calculate(
                    face_match=match,
                    is_live=is_live,
                    has_motion=has_motion
                )
                
                # Make decision
                decision = self.decision_engine.decide(risk)
                
                # Execute decision
                await self.execute_decision(decision, face_data, risk)
                
        else:
            # No face detected - check if system should lock
            self.consecutive_unknown += 1
            if self.consecutive_unknown >= self.config.lock_on_unknown_threshold:
                await self.action_handler.lock_system()
                
    async def execute_decision(self, decision, face_data, risk):
        """Execute security decision"""
        if decision == "ALLOW":
            await self.action_handler.allow_access(face_data)
            self.consecutive_unknown = 0
            
        elif decision == "ALERT":
            await self.alert_router.send_alerts(face_data, risk)
            await self.event_bus.emit_async(Event(
                EventType.INTRUDER_DETECTED,
                {"face": face_data, "risk": risk}
            ))
            
        elif decision == "LOCK":
            await self.action_handler.lock_system()
            await self.alert_router.send_emergency_alerts(face_data, risk)
            
    def stop(self):
        """Stop the security engine"""
        self.running = False
        if self.camera:
            self.camera.stop()
        self.event_bus.stop()