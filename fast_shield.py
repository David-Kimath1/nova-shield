#!/usr/bin/env python3
"""Optimized NOVA-SHIELD with faster face detection"""

from flask import Flask, Response, render_template_string, jsonify
import cv2
import face_recognition
import pickle
import numpy as np
from pathlib import Path
import time
import json
from datetime import datetime

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

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Smaller for speed
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

current_face = {"status": "scanning", "name": None, "confidence": 0}
frame_count = 0

def process_fast(frame):
    global frame_count, current_face
    frame_count += 1
    
    # Process only 1 in 5 frames for speed
    if frame_count % 5 != 0:
        return frame, current_face
    
    # Use smaller image for detection
    small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    
    # Detect faces (use HOG model - faster)
    locations = face_recognition.face_locations(rgb, model="hog")
    
    if not locations:
        current_face = {"status": "no_face", "name": None, "confidence": 0}
        return frame, current_face
    
    # Get encoding for first face only
    encodings = face_recognition.face_encodings(rgb, locations)
    
    if encodings and known_encodings:
        distances = face_recognition.face_distance(known_encodings, encodings[0])
        best_idx = np.argmin(distances)
        confidence = 1 - distances[best_idx]
        
        if confidence > 0.55:  # Lower threshold for speed
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
    
    # Scale coordinates back
    top, right, bottom, left = locations[0]
    top, right, bottom, left = top*4, right*4, bottom*4, left*4
    
    # Draw rectangle
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return frame, current_face

def generate_video():
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        processed, _ = process_fast(frame)
        ret, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>NOVA-SHIELD</title>
    <style>
        body {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            font-family: monospace;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .video-box {
            background: black;
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #e94560;
        }
        .video-feed {
            width: 100%;
        }
        .status {
            background: #0f3460;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            text-align: center;
        }
        .recognized {
            background: #2e7d32;
            color: #a5d6a7;
            padding: 15px;
            border-radius: 8px;
        }
        .unknown {
            background: #c62828;
            color: #ef9a9a;
            padding: 15px;
            border-radius: 8px;
        }
        .scanning {
            background: #ff8f00;
            color: #fff3e0;
            padding: 15px;
            border-radius: 8px;
        }
        h1 {
            color: #e94560;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>[SHIELD] NOVA-SHIELD</h1>
        <div class="video-box">
            <img class="video-feed" src="/video_feed">
        </div>
        <div class="status" id="status">
            <div class="scanning">[SCAN] Looking for face...</div>
        </div>
        <p>[INFO] Look at camera | Green=You | Red=Unknown</p>
    </div>
    <script>
        setInterval(async () => {
            const res = await fetch('/api/status');
            const data = await res.json();
            const statusDiv = document.getElementById('status');
            if (data.status === 'recognized') {
                statusDiv.innerHTML = `<div class="recognized">[OK] Welcome ${data.name} (${data.confidence}%)</div>`;
            } else if (data.status === 'unknown') {
                statusDiv.innerHTML = '<div class="unknown">[WARN] Unknown face detected</div>';
            } else {
                statusDiv.innerHTML = '<div class="scanning">[SCAN] Looking for face...</div>';
            }
        }, 500);
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
    print("[START] Optimized NOVA-SHIELD")
    print("[URL] http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
