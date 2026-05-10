#!/usr/bin/env python3
"""Advanced WebSocket Dashboard for NOVA-SHIELD"""

import json
import time
import psutil
import GPUtil
from datetime import datetime
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import queue

app = Flask(__name__, static_folder='react_build/static', template_folder='react_build')
app.config['SECRET_KEY'] = 'nova-shield-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Event queue for real-time updates
event_queue = queue.Queue()

class DashboardData:
    def __init__(self):
        self.security_score = 95
        self.threat_level = "GREEN"
        self.current_face = None
        self.gpu_available = False
        self.fps = 0
        self.recent_events = []
        self.intruder_count = 0
        
    def to_dict(self):
        return {
            'security_score': self.security_score,
            'threat_level': self.threat_level,
            'current_face': self.current_face,
            'gpu_available': self.gpu_available,
            'fps': self.fps,
            'intruder_count': self.intruder_count,
            'recent_events': self.recent_events[-10:],
            'timestamp': datetime.now().isoformat()
        }

dashboard = DashboardData()

def system_monitor():
    """Background thread for system monitoring"""
    while True:
        try:
            # GPU monitoring
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    dashboard.gpu_available = True
                    gpu_info = {
                        'name': gpus[0].name,
                        'load': f"{gpus[0].load*100:.1f}%",
                        'memory': f"{gpus[0].memoryUsed}/{gpus[0].memoryTotal}MB"
                    }
                else:
                    dashboard.gpu_available = False
                    gpu_info = None
            except:
                dashboard.gpu_available = False
                gpu_info = None
            
            # CPU monitoring
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Emit system stats
            socketio.emit('system_stats', {
                'cpu': cpu_percent,
                'memory': memory.percent,
                'gpu': gpu_info,
                'timestamp': time.time()
            })
            
            time.sleep(2)
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(5)

@socketio.on('connect')
def handle_connect():
    print('[WS] Client connected')
    emit('connected', {'status': 'Connected to NOVA-SHIELD'})
    emit('dashboard_data', dashboard.to_dict())

@socketio.on('request_intruders')
def handle_intruder_request():
    """Send intruder images list"""
    from pathlib import Path
    intruders = []
    intruder_dir = Path('storage/intruders')
    if intruder_dir.exists():
        for img in sorted(intruder_dir.glob('*.jpg'), reverse=True)[:20]:
            intruders.append({
                'path': f"/intruders/{img.name}",
                'timestamp': img.stat().st_mtime
            })
    emit('intruder_list', intruders)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/intruders/<path:filename>')
def serve_intruder(filename):
    return send_from_directory('storage/intruders', filename)

@app.route('/api/stats')
def api_stats():
    return json.dumps(dashboard.to_dict())

def run_dashboard():
    """Start the WebSocket server"""
    # Start system monitor thread
    monitor_thread = threading.Thread(target=system_monitor, daemon=True)
    monitor_thread.start()
    
    print("[DASH] Starting advanced dashboard on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    run_dashboard()
