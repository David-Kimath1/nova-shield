"""Learns user behavior patterns for anomaly detection"""

import json
from datetime import datetime, time
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any


class BehaviorModel:
    """Models normal user behavior"""
    
    def __init__(self, config):
        self.config = config
        self.profile_path = Path(__file__).parent / "profile_store.json"
        self.profile = self._load_profile()
        
    def _load_profile(self) -> Dict:
        """Load behavioral profile"""
        if self.profile_path.exists():
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        return self._default_profile()
        
    def _default_profile(self) -> Dict:
        """Create default profile"""
        return {
            'login_times': [],
            'session_durations': [],
            'active_hours': [],
            'login_count': 0,
            'total_sessions': 0
        }
        
    def record_login(self, timestamp: datetime = None):
        """Record a successful login event"""
        if timestamp is None:
            timestamp = datetime.now()
            
        self.profile['login_times'].append(timestamp.isoformat())
        self.profile['login_count'] += 1
        
        # Keep only last 100 entries
        if len(self.profile['login_times']) > 100:
            self.profile['login_times'] = self.profile['login_times'][-100:]
            
        self._save_profile()
        
    def record_session_end(self, duration_minutes: float):
        """Record session duration"""
        self.profile['session_durations'].append(duration_minutes)
        self.profile['total_sessions'] += 1
        
        # Keep only last 100 entries
        if len(self.profile['session_durations']) > 100:
            self.profile['session_durations'] = self.profile['session_durations'][-100:]
            
        self._save_profile()
        
    def calculate_anomaly_score(self, current_time: datetime = None) -> float:
        """
        Calculate anomaly score (0 = normal, 1 = highly anomalous)
        """
        if current_time is None:
            current_time = datetime.now()
            
        score = 0.0
        weights = {'hour': 0.4, 'day': 0.3, 'frequency': 0.3}
        
        # Check unusual hour
        current_hour = current_time.hour
        usual_hours = self._get_usual_hours()
        
        if usual_hours and current_hour not in usual_hours:
            # How unusual is this hour?
            hour_diff = min(abs(current_hour - h) for h in usual_hours)
            score += weights['hour'] * min(hour_diff / 12, 1.0)
            
        # Check unusual day
        current_weekday = current_time.weekday()
        usual_days = self._get_usual_days()
        
        if usual_days and current_weekday not in usual_days:
            score += weights['day'] * 0.5
            
        # Check frequency anomaly (too many logins)
        recent_logins = self._get_recent_logins(hours=24)
        expected_rate = self._get_expected_login_rate()
        
        if expected_rate > 0 and recent_logins > expected_rate * 2:
            frequency_ratio = recent_logins / expected_rate
            score += weights['frequency'] * min((frequency_ratio - 1) / 3, 1.0)
            
        return min(score, 1.0)
        
    def _get_usual_hours(self) -> set:
        """Get hours with frequent logins"""
        hour_counts = defaultdict(int)
        
        for time_str in self.profile['login_times']:
            try:
                dt = datetime.fromisoformat(time_str)
                hour_counts[dt.hour] += 1
            except:
                pass
                
        # Hours with more than 10% of total logins
        total = sum(hour_counts.values())
        if total == 0:
            return set()
            
        threshold = total * 0.1
        return {h for h, count in hour_counts.items() if count >= threshold}
        
    def _get_usual_days(self) -> set:
        """Get days with frequent logins"""
        day_counts = defaultdict(int)
        
        for time_str in self.profile['login_times']:
            try:
                dt = datetime.fromisoformat(time_str)
                day_counts[dt.weekday()] += 1
            except:
                pass
                
        total = sum(day_counts.values())
        if total == 0:
            return set()
            
        threshold = total * 0.1
        return {d for d, count in day_counts.items() if count >= threshold}
        
    def _get_recent_logins(self, hours: int = 24) -> int:
        """Count logins in recent hours"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        count = 0
        
        for time_str in self.profile['login_times']:
            try:
                dt = datetime.fromisoformat(time_str)
                if dt.timestamp() > cutoff:
                    count += 1
            except:
                pass
                
        return count
        
    def _get_expected_login_rate(self) -> float:
        """Get expected logins per 24 hours"""
        if len(self.profile['login_times']) < 10:
            return 0
            
        # Average logins per day over last 7 days
        cutoff = datetime.now().timestamp() - (7 * 86400)
        recent_count = 0
        
        for time_str in self.profile['login_times']:
            try:
                dt = datetime.fromisoformat(time_str)
                if dt.timestamp() > cutoff:
                    recent_count += 1
            except:
                pass
                
        return recent_count / 7.0
        
    def _save_profile(self):
        """Save behavioral profile to disk"""
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=2)