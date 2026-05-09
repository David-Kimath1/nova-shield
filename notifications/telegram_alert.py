"""Telegram bot integration for alerts"""

import aiohttp
import asyncio
from pathlib import Path
from app.logger import get_logger


class TelegramAlert:
    """Send alerts via Telegram bot"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.logger = get_logger(__name__)
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def send_message(self, message: str) -> bool:
        """Send text message"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        self.logger.info("[TELEGRAM] Message sent")
                        return True
                    else:
                        self.logger.error(f"[TELEGRAM] Failed: {resp.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"[TELEGRAM] Error: {e}")
            return False
            
    async def send_photo(self, photo_path: Path, caption: str = None) -> bool:
        """Send photo with caption"""
        try:
            url = f"{self.base_url}/sendPhoto"
            
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('chat_id', self.chat_id)
                if caption:
                    data.add_field('caption', caption)
                data.add_field('photo', open(photo_path, 'rb'))
                
                async with session.post(url, data=data) as resp:
                    if resp.status == 200:
                        self.logger.info("[TELEGRAM] Photo sent")
                        return True
                    else:
                        self.logger.error(f"[TELEGRAM] Failed: {resp.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"[TELEGRAM] Error: {e}")
            return False
            
    async def send_alert(self, title: str, message: str, snapshot_path: Path = None) -> bool:
        """Send formatted alert"""
        alert_text = f"<b>[ALERT] {title}</b>\n\n{message}"
        
        if snapshot_path and snapshot_path.exists():
            return await self.send_photo(snapshot_path, alert_text)
        else:
            return await self.send_message(alert_text)