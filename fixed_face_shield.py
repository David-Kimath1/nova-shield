#!/usr/bin/env python3
"""Fixed NOVA-SHIELD with better face detection"""

from flask import Flask, Response, render_template_string, jsonify
import cv2
import face_recognition
import pickle
import numpy as np
from pathlib import Path
import time

app = Flask(__name__)

# Load registered face
known_encodings = []
known_names = []

known_file = Path("storage/known_faces.pkl")
if known_file.exists():
    with open(known_file, 'rb') as f:
        data = pickle.load(f)
        known_encodings = data['encodings']
        known_names = data['names']
    print(f"[INFO] Loaded {len(known_names)} faces")
else:
    print("[ERROR] No face registered. Run: python3 register_first_face.py")

# Better camera settings
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)

current_face = {"status": "scanning", "name": None, "confidence": 0}

def detect_and_recognize(frame):
    """Enhanced face detection"""
    global current_face
    
    # Convert to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect all faces
    face_locations = face_recognition.face_locations(rgb, model="hog")
    
    if not face_locations:
        current_face = {"status": "no_face", "name": None, "confidence": 0}
        return frame
    
    # Get encodings for all faces
    face_encodings = face_recognition.face_encodings(rgb, face_locations)
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if matches known face
        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_idx = np.argmin(distances)
            confidence = 1 - distances[best_idx]
            
            if confidence > 0.55:
                current_face = {
                    "status": "recognized",
                    "name": known_names[best_idx],
                    "confidence": round(confidence * 100, 1)
                }
                color = (0, 255, 0)
                label = f"{known_names[best_idx]} ({confidence*100:.0f}%)"
            else:
                current_face = {"status": "unknown", "name": None, "confidence": 0}
                color = (0, 0, 255)
                label = "UNKNOWN"
        else:
            current_face = {"status": "unknown", "name": None, "confidence": 0}
            color = (0, 0, 255)
            label = "UNKNOWN"
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw face center
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        cv2.circle(frame, (center_x, center_y), 3, (255, 255, 255), -1)
    
    return frame

def generate_video():
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        processed = detect_and_recognize(frame)
        
        # Add status text
        if current_face["status"] == "recognized":
            cv2.putText(processed, "FACE VERIFIED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        elif current_face["status"] == "unknown":
            cv2.putText(processed, "UNKNOWN FACE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(processed, "NO FACE DETECTED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        
        # Encode
        ret, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 80])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>NOVA-SHIELD</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            font-family: 'Segoe UI', monospace;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            width: 100%;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #e94560;
            font-size: 36px;
        }
        .header p {
            color: #888;
            margin-top: 10px;
        }
        .video-container {
            background: #000;
            border-radius: 15px;
            overflow: hidden;
            border: 3px solid #e94560;
            box-shadow: 0 10px 40px rgba(233, 69, 96, 0.3);
        }
        .video-feed {
            width: 100%;
            display: block;
        }
        .status-panel {
            margin-top: 20px;
            background: rgba(15, 52, 96, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .status-text {
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
            border-radius: 8px;
        }
        .status-recognized {
            background: #2e7d32;
            color: #a5d6a7;
        }
        .status-unknown {
            background: #c62828;
            color: #ef9a9a;
        }
        .status-no_face {
            background: #ff8f00;
            color: #fff3e0;
        }
        .status-scanning {
            background: #1565c0;
            color: #90caf9;
        }
        .guide {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            font-size: 14px;
            color: #aaa;
        }
        .guide-item {
            display: inline-block;
            margin: 0 15px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>[SHIELD] NOVA-SHIELD</h1>
            <p>Face Recognition Security System</p>
        </div>
        
        <div class="video-container">
            <img class="video-feed" src="/video_feed" id="videoFeed">
        </div>
        
        <div class="status-panel">
            <div id="statusDisplay" class="status-text status-scanning">
                [SCAN] Initializing camera...
            </div>
        </div>
        
        <div class="guide">
            <div class="guide-item">[FACE] Look directly at camera</div>
            <div class="guide-item">[GREEN] You are recognized</div>
            <div class="guide-item">[RED] Unknown person</div>
            <div class="guide-item">[YELLOW] No face detected</div>
        </div>
    </div>
    
    <script>
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                const statusDiv = document.getElementById('statusDisplay');
                
                if (data.status === 'recognized') {
                    statusDiv.className = 'status-text status-recognized';
                    statusDiv.innerHTML = `[OK] WELCOME ${data.name} | Confidence: ${data.confidence}%`;
                } else if (data.status === 'unknown') {
                    statusDiv.className = 'status-text status-unknown';
                    statusDiv.innerHTML = '[WARN] UNKNOWN FACE DETECTED';
                } else if (data.status === 'no_face') {
                    statusDiv.className = 'status-text status-no_face';
                    statusDiv.innerHTML = '[CAMERA] NO FACE DETECTED - Please look at camera';
                } else {
                    statusDiv.className = 'status-text status-scanning';
                    statusDiv.innerHTML = '[SCAN] Scanning for face...';
                }
            } catch(e) {
                console.error('Status error:', e);
            }
        }
        
        // Update every second
        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>'''

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def api_status():
    return jsonify(current_face)

if __name__ == '__main__':
    print("="*50)
    print("NOVA-SHIELD Face Recognition System")
    print("="*50)
    print("[INFO] Make sure you're facing the camera")
    print("[INFO] Good lighting helps recognition")
    print("[INFO] Green box = You are recognized")
    print("[URL] http://localhost:8080")
    print("="*50)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
