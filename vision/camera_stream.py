"""Webcam handling with async support"""

import asyncio
import cv2
from threading import Thread
from queue import Queue
from app.logger import get_logger


class CameraStream:
    """Async camera stream handler"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.cap = None
        self.frame_queue = Queue(maxsize=2)
        self.running = False
        self.thread = None
        
    async def start(self) -> bool:
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.config.camera_id)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            
            if not self.cap.isOpened():
                self.logger.error("[FAIL] Cannot open camera")
                return False
                
            self.running = True
            self.thread = Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            self.logger.info("[CAM] Camera started")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Camera start failed: {e}")
            return False
            
    def _capture_loop(self):
        """Capture frames in separate thread"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except:
                        pass
                self.frame_queue.put(frame)
            else:
                self.logger.warning("[WARN] Failed to capture frame")
                asyncio.sleep(0.1)
                
    async def read(self):
        """Read next frame asynchronously"""
        if not self.running:
            return None
            
        try:
            # Non-blocking queue get
            return await asyncio.get_event_loop().run_in_executor(
                None, self.frame_queue.get, True, 0.033
            )
        except:
            return None
            
    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.cap:
            self.cap.release()
        self.logger.info("[CAM] Camera stopped")