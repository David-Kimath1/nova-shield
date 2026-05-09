"""Routes alerts to appropriate channels"""

from app.logger import get_logger
from app.event_bus import EventBus, Event, EventType
from notifications.telegram_alert import TelegramAlert
from notifications.sms_alert import SMSAlert


class AlertRouter:
    """Routes alerts to configured notification channels"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = get_logger(__name__)
        
        # Initialize alert channels
        self.telegram = None
        self.sms = None
        
        if config.telegram_enabled and config.telegram_bot_token:
            self.telegram = TelegramAlert(
                config.telegram_bot_token,
                config.telegram_chat_id
            )
            
        if config.sms_enabled and config.africas_talking_api_key:
            self.sms = SMSAlert(
                config.africas_talking_api_key,
                config.africas_talking_username,
                config.alert_phone_number
            )
            
        # Subscribe to events
        event_bus.subscribe(EventType.INTRUDER_DETECTED, self.on_intruder)
        event_bus.subscribe(EventType.SPOOF_ATTEMPT, self.on_spoof)
        event_bus.subscribe(EventType.SYSTEM_LOCK, self.on_lock)
        
    async def on_intruder(self, event: Event):
        """Handle intruder detection event"""
        data = event.data
        await self.send_alerts(
            title="Intruder Detected",
            message=f"Unknown person detected. Risk level: {data.get('risk', 'MEDIUM')}",
            snapshot=data.get('face', {}).get('image'),
            is_emergency=data.get('risk', 0.5) > 0.8
        )
        
    async def on_spoof(self, event: Event):
        """Handle spoof attempt event"""
        await self.send_alerts(
            title="Spoofing Attempt Detected",
            message="Someone attempted to bypass liveness detection",
            is_emergency=True
        )
        
    async def on_lock(self, event: Event):
        """Handle system lock event"""
        await self.send_alerts(
            title="System Locked",
            message="System locked due to security threat",
            is_emergency=False
        )
        
    async def send_alerts(self, title: str, message: str, 
                          snapshot=None, is_emergency: bool = False):
        """Send alerts through all configured channels"""
        
        # Send to Telegram if enabled
        if self.telegram:
            await self.telegram.send_alert(title, message, snapshot)
            
        # Send SMS for emergencies
        if is_emergency and self.sms:
            await self.sms.send_emergency_alert({
                'title': title,
                'message': message,
                'risk_score': 'HIGH' if is_emergency else 'MEDIUM',
                'timestamp': str(datetime.now())
            })
            
        self.logger.info(f"[ALERT] Sent: {title}")