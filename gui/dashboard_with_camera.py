#!/usr/bin/env python3
"""Web dashboard with live camera feed"""

from flask import Flask, render_template, Response, jsonify
import cv2
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config

app = Flask(__name__)
config = Config()

# Global camera object
camera = None

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(config.camera_id)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height)
    return camera

def generate_frames():
    """Generate MJPEG frames for video feed"""
    cam = get_camera()
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NOVA-SHIELD Dashboard</title>
        <style>
            body {
                font-family: monospace;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #e94560;
                border-bottom: 2px solid #e94560;
                padding-bottom: 10px;
            }
            .video-container {
                background: black;
                border-radius: 10px;
                overflow: hidden;
                margin: 20px 0;
                border: 2px solid #e94560;
            }
            .video-feed {
                width: 100%;
                height: auto;
            }
            .status {
                background: #0f3460;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .status h3 {
                margin: 0 0 10px 0;
                color: #e94560;
            }
            .status-item {
                display: inline-block;
                margin-right: 30px;
                padding: 10px;
            }
            .status-label {
                font-weight: bold;
                color: #888;
            }
            .status-value {
                color: #4caf50;
                font-size: 24px;
                font-weight: bold;
            }
            .btn {
                background: #e94560;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            .btn:hover {
                background: #c7354f;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ NOVA-SHIELD Security Dashboard</h1>
            
            <div class="video-container">
                <img class="video-feed" src="/video_feed" alt="Camera Feed">
            </div>
            
            <div class="status">
                <h3>System Status</h3>
                <div class="status-item">
                    <div class="status-label">Camera</div>
                    <div class="status-value" id="camera-status">CHECKING...</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Face Detection</div>
                    <div class="status-value" id="face-status">INACTIVE</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Security Level</div>
                    <div class="status-value" id="security-status">MONITORING</div>
                </div>
            </div>
            
            <button class="btn" onclick="location.reload()">🔄 Refresh</button>
            <button class="btn" onclick="window.open('/video_feed')">📹 Open Camera Feed</button>
            
            <p style="margin-top: 20px; font-size: 12px; color: #888;">
                NOVA-SHIELD Active | Face Recognition Ready
            </p>
        </div>
        
        <script>
            // Simulate status updates
            setInterval(() => {
                document.getElementById('camera-status').innerHTML = 'ACTIVE ✓';
                document.getElementById('camera-status').style.color = '#4caf50';
            }, 1000);
        </script>
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """Return system status as JSON"""
    cam = get_camera()
    return jsonify({
        'camera_connected': cam.isOpened(),
        'system': 'running'
    })

if __name__ == '__main__':
    print("[DASH] Starting dashboard at http://localhost:8080")
    print("[DASH] Camera feed at http://localhost:8080/video_feed")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
