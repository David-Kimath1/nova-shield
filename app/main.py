#!/usr/bin/env python3
"""
NOVA-SHIELD Daemon - Main Entry Point
Runs as systemd service for continuous security monitoring
"""

import sys
import signal
import time
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.logger import setup_logger, get_logger
from app.event_bus import EventBus
from core.engine import SecurityEngine
from hardware.backend_selector import BackendSelector


class NovaShieldDaemon:
    """Main daemon controller"""
    
    def __init__(self):
        self.config = Config()
        self.logger = get_logger(__name__)
        self.event_bus = EventBus()
        self.running = True
        self.engine = None
        
    def setup_signal_handlers(self):
        """Handle shutdown signals"""
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
        
    def shutdown(self, signum, frame):
        """Graceful shutdown"""
        self.logger.info("[LOCK] Shutting down NOVA-SHIELD...")
        self.running = False
        if self.engine:
            self.engine.stop()
        sys.exit(0)
        
    async def initialize(self):
        """Initialize all components"""
        self.logger.info("[SHIELD] NOVA-SHIELD Initializing...")
        
        # Detect hardware and select backend
        backend = BackendSelector()
        device = backend.select_backend()
        
        # Initialize security engine
        self.engine = SecurityEngine(
            config=self.config,
            event_bus=self.event_bus,
            device=device
        )
        
        if not await self.engine.initialize():
            self.logger.error("[FAIL] Failed to initialize security engine")
            return False
            
        self.logger.info("[OK] NOVA-SHIELD Ready")
        return True
        
    async def run(self):
        """Main daemon loop"""
        if not await self.initialize():
            return
            
        self.logger.info("[RUN] Security engine running...")
        
        while self.running:
            try:
                await self.engine.process_frame()
                await asyncio.sleep(0.033)  # ~30 FPS
            except Exception as e:
                self.logger.error(f"[ERROR] Error in main loop: {e}")
                await asyncio.sleep(1)
                
    def start(self):
        """Start the daemon"""
        self.setup_signal_handlers()
        asyncio.run(self.run())


if __name__ == "__main__":
    daemon = NovaShieldDaemon()
    daemon.start()