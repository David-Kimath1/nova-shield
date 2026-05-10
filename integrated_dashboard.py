from flask import Flask, Response, render_template_string, jsonify
import cv2
import face_recognition
import pickle
import numpy as np
from pathlib import Path
import time
import json

app = Flask(__name__)

# Load your registered face
known_encodings = []
known_names = []

known_file = Path("storage/known_faces.pkl")
if known_file.exists():
    with open(known_file, 'rb') as f:
        data = pickle.load(f)
        known_encodings = data['encodings']
        known_names = data['names']
    print(f"[INFO] Loaded {len(known_names)} registered faces")
else:
    print("[WARN] No registered faces. Run register_first_face.py first")

camera = cv2.VideoCapture(0)
current_face = {"name": None, "confidence": 0, "status": "scanning"}

def detect_faces():
    global current_face
    frame_count = 0
    
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        # Process every 5th frame for performance
        frame_count += 1
        if frame_count % 5 != 0:
            yield frame
            continue
            
        # Resize for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            current_face = {"name": None, "confidence": 0, "status": "no_face"}
            yield frame
            continue
            
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            if known_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                distances = face_recognition.face_distance(known_encodings, face_encoding)
                
                if True in matches:
                    best_idx = np.argmin(distances)
                    confidence = 1 - distances[best_idx]
                    
                    if confidence > 0.6:
                        current_face = {
                            "name": known_names[best_idx],
                            "confidence": round(confidence * 100, 1),
                            "status": "recognized"
                        }
                    else:
                        current_face = {
                            "name": "unknown",
                            "confidence": round(confidence * 100, 1),
                            "status": "unknown"
                        }
                else:
                    current_face = {
                        "name": "unknown",
                        "confidence": 0,
                        "status": "unknown"
                    }
            else:
                current_face = {
                    "name": "unknown",
                    "confidence": 0,
                    "status": "unknown"
                }
            
            # Draw rectangle
            top, right, bottom, left = [int(x * 2) for x in face_locations[0]]
            color = (0, 255, 0) if current_face["status"] == "recognized" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label
            label = f"{current_face['name']} ({current_face['confidence']}%)" if current_face['name'] else "Unknown"
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        yield frame

def generate_video():
    for frame in detect_faces():
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>NOVA-SHIELD Face Recognition</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: rgba(15, 52, 96, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #0f3460;
        }
        .header h1 {
            color: #e94560;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .video-container {
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            border: 2px solid #e94560;
        }
        .video-feed {
            width: 100%;
            height: auto;
            display: block;
        }
        .status-panel {
            background: rgba(15, 52, 96, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #0f3460;
        }
        .face-status {
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .recognized {
            background: #2e7d32;
            color: #a5d6a7;
        }
        .unknown {
            background: #c62828;
            color: #ef9a9a;
        }
        .no-face {
            background: #ff8f00;
            color: #fff3e0;
        }
        .scanning {
            background: #1565c0;
            color: #90caf9;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #0f3460;
        }
        .info-label {
            font-weight: bold;
            color: #888;
        }
        .info-value {
            color: #e94560;
            font-family: monospace;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                <span>[SHIELD]</span> NOVA-SHIELD
            </h1>
            <p>AI-Powered Biometric Security System</p>
        </div>
        
        <div class="video-container">
            <img class="video-feed" src="/video_feed" id="videoFeed">
        </div>
        
        <div class="status-panel">
            <div class="face-status" id="faceStatus">
                [SCANNING] Looking for face...
            </div>
            
            <div class="info-row">
                <span class="info-label">[FACE] Current User</span>
                <span class="info-value" id="userName">-</span>
            </div>
            <div class="info-row">
                <span class="info-label">[PERCENT] Confidence</span>
                <span class="info-value" id="confidence">-</span>
            </div>
            <div class="info-row">
                <span class="info-label">[CAMERA] Status</span>
                <span class="info-value" id="cameraStatus">Active</span>
            </div>
            <div class="info-row">
                <span class="info-label">[LOCK] Security Level</span>
                <span class="info-value" id="securityLevel">Monitoring</span>
            </div>
        </div>
        
        <div class="footer">
            [INFO] System Active | [FACE] Face Recognition Ready | [SHIELD] Continuous Verification
        </div>
    </div>
    
    <script>
        const eventSource = new EventSource('/stream_status');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const statusDiv = document.getElementById('faceStatus');
            const userNameSpan = document.getElementById('userName');
            const confidenceSpan = document.getElementById('confidence');
            
            if (data.status === 'recognized') {
                statusDiv.className = 'face-status recognized';
                statusDiv.innerHTML = '[CHECK] FACE RECOGNIZED - Access Granted';
                userNameSpan.innerHTML = data.name;
                confidenceSpan.innerHTML = data.confidence + '%';
            } else if (data.status === 'unknown') {
                statusDiv.className = 'face-status unknown';
                statusDiv.innerHTML = '[WARN] UNKNOWN FACE DETECTED';
                userNameSpan.innerHTML = 'Unknown Person';
                confidenceSpan.innerHTML = '0%';
            } else if (data.status === 'no_face') {
                statusDiv.className = 'face-status no-face';
                statusDiv.innerHTML = '[CAMERA] No Face Detected';
                userNameSpan.innerHTML = '-';
                confidenceSpan.innerHTML = '-';
            } else {
                statusDiv.className = 'face-status scanning';
                statusDiv.innerHTML = '[SCAN] Scanning for face...';
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream_status')
def stream_status():
    def generate():
        while True:
            data = json.dumps(current_face)
            yield f"data: {data}\n\n"
            time.sleep(0.5)
    return Response(generate(), mimetype="text/event-stream")

if __name__ == '__main__':
    print("[START] NOVA-SHIELD Face Recognition Dashboard")
    print("[URL] Open http://localhost:8080 in your browser")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
