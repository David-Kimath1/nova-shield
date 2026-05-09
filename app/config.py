"""Global configuration management"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Central configuration manager"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
            
        load_dotenv()
        self.load_config(config_path)
        
    def load_config(self, config_path):
        """Load YAML configuration"""
        with open(config_path, 'r') as f:
            self.data = yaml.safe_load(f)
            
    @property
    def camera_id(self):
        return self.data.get('camera', {}).get('device_id', 0)
    
    @property
    def camera_width(self):
        return self.data.get('camera', {}).get('width', 640)
    
    @property
    def camera_height(self):
        return self.data.get('camera', {}).get('height', 480)
    
    @property
    def recognition_threshold(self):
        return self.data.get('recognition', {}).get('threshold', 0.6)
    
    @property
    def lock_on_unknown_threshold(self):
        return self.data.get('security', {}).get('lock_on_unknown_threshold', 3)
    
    @property
    def telegram_enabled(self):
        return self.data.get('notifications', {}).get('telegram', {}).get('enabled', False)
    
    @property
    def telegram_bot_token(self):
        return os.getenv('TELEGRAM_BOT_TOKEN')
    
    @property
    def telegram_chat_id(self):
        return os.getenv('TELEGRAM_CHAT_ID')
    
    @property
    def sms_enabled(self):
        return self.data.get('notifications', {}).get('sms', {}).get('enabled', False)
    
    @property
    def africas_talking_api_key(self):
        return os.getenv('AFRICASTALKING_API_KEY')
    
    @property
    def africas_talking_username(self):
        return os.getenv('AFRICASTALKING_USERNAME')
    
    @property
    def alert_phone_number(self):
        return os.getenv('ALERT_PHONE_NUMBER')
    
    @property
    def storage_path(self):
        return Path(self.data.get('storage', {}).get('path', './storage'))
    
    @property
    def gpu_enabled(self):
        return self.data.get('hardware', {}).get('gpu', {}).get('enabled', True)
    
    @property
    def behavior_learning_enabled(self):
        return self.data.get('ai', {}).get('behavior_learning', True)