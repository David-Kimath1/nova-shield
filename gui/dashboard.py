"""Web dashboard for NOVA-SHIELD"""

from flask import Flask, render_template, jsonify, Response
from flask_socketio import SocketIO, emit
import cv2
import json
from pathlib import Path
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from security.intrusion_logger import IntrusionLogger
from vision.camera_stream import CameraStream

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nova-shield-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

config = Config()
intrusion_logger = IntrusionLogger(config)
camera_stream = None


def get_camera():
    """Get camera stream instance"""
    global camera_stream
    if camera_stream is None:
        camera_stream = CameraStream(config)
        camera_stream.start()
    return camera_stream


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/alerts')
def alerts_page():
    """Alerts history page"""
    return render_template('alerts.html')


@app.route('/api/status')
def api_status():
    """Get current system status"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'camera_active': camera_stream is not None
    })


@app.route('/api/intrusions')
def api_intrusions():
    """Get intrusion logs"""
    limit = request.args.get('limit', 50, type=int)
    intrusions = intrusion_logger.get_recent_intrusions(limit)
    return jsonify(intrusions)


@app.route('/api/stats')
def api_stats():
    """Get system statistics"""
    intrusions = intrusion_logger.get_recent_intrusions(1000)
    
    stats = {
        'total_intrusions': len(intrusions),
        'high_risk_count': len([i for i in intrusions if i.get('risk_score', 0) > 0.6]),
        'last_24h': len([i for i in intrusions 
                        if (datetime.now() - datetime.fromisoformat(i['timestamp'])).days < 1])
    }
    
    return jsonify(stats)


@app.route('/video_feed')
def video_feed():
    """MJPEG video stream"""
    def generate():
        camera = get_camera()
        while True:
            frame = camera.read()
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'data': 'Connected to NOVA-SHIELD'})


def run_dashboard():
    """Run the dashboard server"""
    socketio.run(app, host=config.data.get('dashboard', {}).get('host', '127.0.0.1'),
                 port=config.data.get('dashboard', {}).get('port', 8080), debug=False)


if __name__ == '__main__':
    run_dashboard()