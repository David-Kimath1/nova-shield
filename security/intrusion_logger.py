"""Logs intrusion attempts and saves snapshots"""

import json
import cv2
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.logger import get_logger


class IntrusionLogger:
    """Logs all security events"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.log_path = config.storage_path / "logs" / "intrusions.json"
        self.snapshot_path = config.storage_path / "intruders"
        
        # Create directories
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.snapshot_path.mkdir(parents=True, exist_ok=True)
        
    def log_intrusion(self, face_data, risk_score: float, action: str) -> Optional[Path]:
        """
        Log an intrusion attempt
        Returns path to saved snapshot
        """
        timestamp = datetime.now()
        
        # Save snapshot
        snapshot_file = None
        if face_data and face_data.image is not None:
            filename = f"intruder_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
            snapshot_file = self.snapshot_path / filename
            cv2.imwrite(str(snapshot_file), face_data.image)
            
        # Create log entry
        entry = {
            'timestamp': timestamp.isoformat(),
            'type': 'intrusion',
            'action': action,
            'risk_score': risk_score,
            'snapshot': str(snapshot_file) if snapshot_file else None,
            'face_details': {
                'has_encoding': face_data.encoding is not None if face_data else False,
                'bounding_box': face_data.bounding_box if face_data else None
            }
        }
        
        # Append to log file
        self._append_log(entry)
        
        self.logger.warning(f"[INTRUSION] Logged intrusion (risk: {risk_score:.2f})")
        return snapshot_file
        
    def log_access(self, status: str, face_data=None):
        """Log access attempt"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'access',
            'status': status,
            'face_detected': face_data is not None
        }
        
        self._append_log(entry)
        self.logger.info(f"[ACCESS] {status}")
        
    def log_system_lock(self):
        """Log system lock event"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'system',
            'event': 'locked',
            'reason': 'security_threat'
        }
        
        self._append_log(entry)
        
    def _append_log(self, entry: dict):
        """Append entry to log file"""
        try:
            if self.log_path.exists():
                with open(self.log_path, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
                
            logs.append(entry)
            
            # Keep last 1000 entries
            if len(logs) > 1000:
                logs = logs[-1000:]
                
            with open(self.log_path, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to write log: {e}")
            
    def get_recent_intrusions(self, limit: int = 50) -> list:
        """Get recent intrusion logs"""
        try:
            if self.log_path.exists():
                with open(self.log_path, 'r') as f:
                    logs = json.load(f)
                    
                intrusions = [l for l in logs if l.get('type') == 'intrusion']
                return intrusions[-limit:]
        except:
            pass
            
        return []