"""SMS gateway integration for Kenya (Africa's Talking)"""

import aiohttp
from app.logger import get_logger


class SMSAlert:
    """Send SMS alerts via Africa's Talking API"""
    
    def __init__(self, api_key: str, username: str, phone_number: str):
        self.api_key = api_key
        self.username = username
        self.phone_number = phone_number
        self.logger = get_logger(__name__)
        self.base_url = "https://api.africastalking.com/version1/messaging"
        
    async def send_sms(self, message: str) -> bool:
        """Send SMS message"""
        try:
            headers = {
                'ApiKey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'username': self.username,
                'to': self.phone_number,
                'message': message[:160]  # SMS length limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, data=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get('SMSMessageData', {}).get('Recipients'):
                            self.logger.info("[SMS] Alert sent")
                            return True
                            
                    self.logger.error(f"[SMS] Failed: {resp.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"[SMS] Error: {e}")
            return False
            
    async def send_emergency_alert(self, intruder_info: dict) -> bool:
        """Send emergency alert for high-risk intrusions"""
        message = (f"EMERGENCY: Intruder detected! "
                   f"Risk: {intruder_info.get('risk_score', 'HIGH')}. "
                   f"Time: {intruder_info.get('timestamp', 'now')}. "
                   f"Action required immediately.")
                   
        return await self.send_sms(message)