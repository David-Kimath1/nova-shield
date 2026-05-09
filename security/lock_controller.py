"""Controls Linux system locking"""

import subprocess
import os
from app.logger import get_logger


class LockController:
    """Controls system locking/unlocking"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.locked = False
        
    def lock(self) -> bool:
        """Lock the system"""
        try:
            # For Cinnamon desktop (Linux Mint)
            subprocess.run(['cinnamon-screensaver-command', '-l'], 
                         check=True, capture_output=True)
            self.locked = True
            self.logger.info("[LOCK] System locked")
            return True
        except subprocess.CalledProcessError:
            try:
                # Fallback for other desktops
                subprocess.run(['loginctl', 'lock-session'], 
                             check=True, capture_output=True)
                self.locked = True
                self.logger.info("[LOCK] System locked (loginctl)")
                return True
            except:
                self.logger.error("[FAIL] Failed to lock system")
                return False
                
    def unlock(self) -> bool:
        """Unlock the system (requires authentication)"""
        # Unlocking is handled by the PAM module
        # This just updates our internal state
        self.locked = False
        self.logger.info("[UNLOCK] System unlocked")
        return True
        
    def is_locked(self) -> bool:
        """Check if system is locked"""
        try:
            result = subprocess.run(
                ['cinnamon-screensaver-command', '-q'],
                capture_output=True, text=True
            )
            return 'active' in result.stdout.lower()
        except:
            return self.locked