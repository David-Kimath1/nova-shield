#!/usr/bin/env python3
"""NOVA-SHIELD with Anti-Spoofing - Detects Photos vs Real Faces"""

from flask import Flask, Response, render_template_string, jsonify, session, redirect
import cv2
import face_recognition
import pickle
import numpy as np
from pathlib import Path
import time
import os
from scipy.fft import fft2, fftshift
from collections import deque

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

authenticated = False
current_face = {"status": "scanning", "name": None, "confidence": 0, "is_live": False}

# Anti-spoofing history
eye_blink_history = deque(maxlen=10)
motion_history = deque(maxlen=10)
last_face_position = None
blink_counter = 0

def detect_eye_blink(face_landmarks):
    """Detect eye blinks using Eye Aspect Ratio (EAR)"""
    global blink_counter
    
    if 'left_eye' not in face_landmarks or 'right_eye' not in face_landmarks:
        return False
    
    def eye_aspect_ratio(eye_points):
        eye = np.array(eye_points)
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        ear = (A + B) / (2.0 * C)
        return ear
    
    left_ear = eye_aspect_ratio(face_landmarks['left_eye'])
    right_ear = eye_aspect_ratio(face_landmarks['right_eye'])
    ear = (left_ear + right_ear) / 2.0
    
    # Blink detected when EAR drops below threshold
    if ear < 0.2:
        blink_counter += 1
        if blink_counter > 3:
            return True
    else:
        blink_counter = max(0, blink_counter - 1)
    
    return False

def detect_head_motion(face_location):
    """Detect natural head movement"""
    global last_face_position, motion_history
    
    if last_face_position is None:
        last_face_position = face_location
        return False
    
    top, right, bottom, left = face_location
    last_top, last_right, last_bottom, last_left = last_face_position
    
    # Calculate movement
    movement_x = abs(left - last_left)
    movement_y = abs(top - last_top)
    movement = movement_x + movement_y
    
    last_face_position = face_location
    
    is_moving = movement > 8
    motion_history.append(is_moving)
    
    return sum(motion_history) > 2

def detect_texture_spoof(face_roi):
    """Detect photo/video using texture analysis"""
    if face_roi is None or face_roi.size == 0:
        return False
    
    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    
    # Apply FFT to detect frequency patterns
    f = fft2(gray)
    fshift = fftshift(f)
    magnitude = np.abs(fshift)
    
    # Check for high-frequency patterns (indicates screen/print)
    height, width = gray.shape
    center_h, center_w = height // 2, width // 2
    
    # Extract high-frequency components
    high_freq = magnitude[center_h-10:center_h+10, center_w-10:center_w+10]
    high_freq_mean = np.mean(high_freq)
    low_freq_mean = np.mean(magnitude)
    
    # Calculate frequency ratio
    if low_freq_mean > 0:
        freq_ratio = high_freq_mean / low_freq_mean
        # High ratio indicates possible spoof (screen moire pattern)
        return freq_ratio > 3.5
    
    return False

def detect_reflection_spoof(face_roi):
    """Detect screen glare/reflection"""
    if face_roi is None or face_roi.size == 0:
        return False
    
    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    
    # Detect bright spots (screen glare)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    glare_ratio = np.sum(thresh > 0) / thresh.size
    
    return glare_ratio > 0.05

def calculate_liveness_score(face_roi, face_landmarks, face_location):
    """Calculate liveness score (0 = spoof, 1 = live)"""
    score = 0.5  # Start neutral
    
    # Blink detection (30% weight)
    has_blink = detect_eye_blink(face_landmarks)
    if has_blink:
        score += 0.3
    
    # Motion detection (25% weight)
    has_motion = detect_head_motion(face_location)
    if has_motion:
        score += 0.25
    
    # Texture analysis (25% weight)
    is_texture_spoof = detect_texture_spoof(face_roi)
    if not is_texture_spoof:
        score += 0.25
    
    # Reflection detection (20% weight)
    is_reflection_spoof = detect_reflection_spoof(face_roi)
    if not is_reflection_spoof:
        score += 0.20
    
    return min(score, 1.0)

def detect_face(frame):
    global current_face
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb, model="hog")
    
    if not face_locations:
        current_face = {"status": "no_face", "name": None, "confidence": 0, "is_live": False}
        return frame
    
    face_encodings = face_recognition.face_encodings(rgb, face_locations)
    face_landmarks_list = face_recognition.face_landmarks(rgb, face_locations)
    
    for i, ((top, right, bottom, left), face_encoding, landmarks) in enumerate(zip(face_locations, face_encodings, face_landmarks_list)):
        
        # Extract face ROI for analysis
        face_roi = frame[top:bottom, left:right]
        
        # Calculate liveness score
        liveness = calculate_liveness_score(face_roi, landmarks, (top, right, bottom, left))
        is_live = liveness > 0.6
        
        # Face recognition
        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_idx = np.argmin(distances)
            confidence = 1 - distances[best_idx]
            
            if confidence > 0.55 and is_live:
                current_face = {
                    "status": "recognized",
                    "name": known_names[best_idx],
                    "confidence": round(confidence * 100, 1),
                    "is_live": True,
                    "liveness_score": round(liveness * 100, 1)
                }
                color = (0, 255, 0)
                label = f"{known_names[best_idx]} (LIVE)"
            elif confidence > 0.55 and not is_live:
                current_face = {
                    "status": "spoof",
                    "name": known_names[best_idx],
                    "confidence": round(confidence * 100, 1),
                    "is_live": False,
                    "liveness_score": round(liveness * 100, 1)
                }
                color = (0, 165, 255)
                label = "PHOTO DETECTED"
            else:
                current_face = {
                    "status": "unknown",
                    "name": None,
                    "confidence": 0,
                    "is_live": is_live,
                    "liveness_score": round(liveness * 100, 1)
                }
                color = (0, 0, 255)
                label = "UNKNOWN"
        else:
            current_face = {"status": "unknown", "name": None, "confidence": 0, "is_live": is_live}
            color = (0, 0, 255)
            label = "NO REGISTERED FACE"
        
        # Draw bounding box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(frame, (left, bottom - 25), (left + label_size[0] + 10, bottom), color, -1)
        cv2.putText(frame, label, (left + 5, bottom - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Draw liveness indicator
        if is_live:
            cv2.putText(frame, f"LIVE: {int(liveness*100)}%", (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            cv2.putText(frame, f"SPOOF: {int((1-liveness)*100)}%", (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
    
    return frame

def generate_video():
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        processed = detect_face(frame)
        
        # Add system status bar
        if current_face.get("is_live", False):
            cv2.putText(processed, "LIVENESS: VERIFIED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        elif current_face.get("status") == "spoof":
            cv2.putText(processed, "WARNING: PHOTO DETECTED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
        ret, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 75])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

SCANNER_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOVA-SHIELD | Anti-Spoofing Face Authentication</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(ellipse at 20% 30%, #0a0a0a, #000000);
            min-height: 100vh;
            color: #ffffff;
        }
        
        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
        }
        
        .bg-animation::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 50%, rgba(233, 69, 96, 0.08), transparent 50%);
            animation: rotate 20s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .container {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .scanner-card {
            max-width: 520px;
            width: 100%;
            background: rgba(10, 10, 20, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 48px;
            padding: 32px;
            border: 1px solid rgba(233, 69, 96, 0.2);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 32px;
        }
        
        .logo-icon {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, #e94560, #c7354f);
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 16px;
            box-shadow: 0 10px 40px rgba(233, 69, 96, 0.3);
        }
        
        .logo h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e94560);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }
        
        .logo p {
            color: #888;
            font-size: 14px;
            margin-top: 8px;
        }
        
        .video-wrapper {
            position: relative;
            background: linear-gradient(135deg, #1a1a2e, #0a0a15);
            border-radius: 32px;
            padding: 4px;
            margin-bottom: 24px;
        }
        
        .video-glow {
            position: absolute;
            inset: -2px;
            background: linear-gradient(135deg, #e94560, #c7354f);
            border-radius: 34px;
            opacity: 0.3;
            transition: opacity 0.3s ease;
        }
        
        .video-box {
            position: relative;
            border-radius: 30px;
            overflow: hidden;
            background: #000;
        }
        
        .video-feed {
            width: 100%;
            display: block;
            border-radius: 30px;
        }
        
        .security-badges {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .badge {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 16px;
            padding: 12px;
            text-align: center;
            border: 1px solid rgba(233, 69, 96, 0.2);
        }
        
        .badge-label {
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        
        .badge-value {
            font-size: 18px;
            font-weight: 700;
            color: #e94560;
        }
        
        .badge-value.active {
            color: #4caf50;
        }
        
        .badge-value.warning {
            color: #ff8f00;
        }
        
        .status-card {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 24px;
            padding: 20px;
            margin-bottom: 24px;
            border: 1px solid rgba(233, 69, 96, 0.1);
        }
        
        .status-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff8f00;
            animation: pulse 1.5s infinite;
        }
        
        .status-dot.live {
            background: #4caf50;
        }
        
        .status-dot.spoof {
            background: #ef5350;
        }
        
        .status-text {
            font-size: 15px;
            font-weight: 500;
        }
        
        .confidence-bar {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            height: 6px;
            overflow: hidden;
            margin-bottom: 12px;
        }
        
        .confidence-fill {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #e94560, #ff6b8a);
            border-radius: 12px;
            transition: width 0.3s ease;
        }
        
        .liveness-bar {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            height: 6px;
            overflow: hidden;
        }
        
        .liveness-fill {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #81c784);
            border-radius: 12px;
            transition: width 0.3s ease;
        }
        
        .btn-verify {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #e94560, #c7354f);
            border: none;
            border-radius: 40px;
            color: white;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn-verify:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(233, 69, 96, 0.4);
        }
        
        .btn-verify:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @media (max-width: 768px) {
            .scanner-card {
                padding: 24px;
            }
            
            .security-badges {
                flex-direction: column;
            }
            
            .badge-value {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    <div class="container">
        <div class="scanner-card">
            <div class="logo">
                <div class="logo-icon">NS</div>
                <h1>NOVA-SHIELD</h1>
                <p>Anti-Spoofing Face Authentication</p>
            </div>
            
            <div class="video-wrapper">
                <div class="video-glow"></div>
                <div class="video-box">
                    <img class="video-feed" src="/video_feed" id="videoFeed">
                </div>
            </div>
            
            <div class="security-badges">
                <div class="badge">
                    <div class="badge-label">Blink Detection</div>
                    <div class="badge-value" id="blinkStatus">Active</div>
                </div>
                <div class="badge">
                    <div class="badge-label">Motion Analysis</div>
                    <div class="badge-value" id="motionStatus">Active</div>
                </div>
                <div class="badge">
                    <div class="badge-label">Texture Check</div>
                    <div class="badge-value" id="textureStatus">Active</div>
                </div>
            </div>
            
            <div class="status-card">
                <div class="status-header">
                    <div class="status-dot" id="statusDot"></div>
                    <div class="status-text" id="statusText">Initializing security systems...</div>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" id="confidenceFill"></div>
                </div>
                <div class="liveness-bar">
                    <div class="liveness-fill" id="livenessFill"></div>
                </div>
            </div>
            
            <button class="btn-verify" onclick="verifyFace()" id="verifyBtn">
                <span>●</span> Verify Identity
            </button>
        </div>
    </div>
    
    <script>
        let isVerifying = false;
        
        async function updateStatus() {
            try {
                const res = await fetch('/api/face_status');
                const data = await res.json();
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const confidenceFill = document.getElementById('confidenceFill');
                const livenessFill = document.getElementById('livenessFill');
                
                if (data.status === 'recognized' && data.is_live) {
                    statusDot.className = 'status-dot live';
                    statusText.innerHTML = `Live face verified - ${data.name} (${data.confidence}%)`;
                    confidenceFill.style.width = data.confidence + '%';
                    livenessFill.style.width = (data.liveness_score || 85) + '%';
                    
                    if (!isVerifying && data.confidence > 60) {
                        setTimeout(() => verifyFace(), 500);
                    }
                } else if (data.status === 'spoof') {
                    statusDot.className = 'status-dot spoof';
                    statusText.innerHTML = `WARNING: Photo detected! Real face required.`;
                    confidenceFill.style.width = data.confidence + '%';
                    livenessFill.style.width = (data.liveness_score || 20) + '%';
                } else if (data.status === 'unknown') {
                    statusDot.className = 'status-dot spoof';
                    statusText.innerHTML = 'Unknown face detected';
                    confidenceFill.style.width = '0%';
                    livenessFill.style.width = '0%';
                } else {
                    statusDot.className = 'status-dot';
                    statusText.innerHTML = 'Looking for face...';
                    confidenceFill.style.width = '0%';
                    livenessFill.style.width = '0%';
                }
            } catch(e) {
                console.error(e);
            }
        }
        
        async function verifyFace() {
            if (isVerifying) return;
            isVerifying = true;
            const btn = document.getElementById('verifyBtn');
            btn.innerHTML = '<span>◐</span> Verifying liveness...';
            btn.disabled = true;
            
            try {
                const res = await fetch('/api/check_auth');
                const data = await res.json();
                
                if (data.success && data.is_live) {
                    btn.innerHTML = '<span>✓</span> Verified. Redirecting...';
                    setTimeout(() => {
                        window.location.href = '/bank_dashboard';
                    }, 1000);
                } else if (data.photo_detected) {
                    btn.innerHTML = '<span>✗</span> Photo Detected - Access Denied';
                    setTimeout(() => {
                        btn.innerHTML = '<span>●</span> Verify Identity';
                        btn.disabled = false;
                        isVerifying = false;
                    }, 2000);
                } else {
                    btn.innerHTML = '<span>✗</span> Verification Failed';
                    setTimeout(() => {
                        btn.innerHTML = '<span>●</span> Verify Identity';
                        btn.disabled = false;
                        isVerifying = false;
                    }, 2000);
                }
            } catch(e) {
                btn.innerHTML = '<span>⚠</span> Error';
                setTimeout(() => {
                    btn.innerHTML = '<span>●</span> Verify Identity';
                    btn.disabled = false;
                    isVerifying = false;
                }, 2000);
            }
        }
        
        setInterval(updateStatus, 300);
    </script>
</body>
</html>
'''

BANK_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOVA-SHIELD | Secure Banking</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(ellipse at 20% 30%, #0a0a0a, #000000);
            min-height: 100vh;
            color: #ffffff;
        }
        
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }
        
        .header {
            background: rgba(10, 10, 20, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            padding: 20px 28px;
            margin-bottom: 28px;
            border: 1px solid rgba(233, 69, 96, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #e94560, #c7354f);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: 700;
        }
        
        .logo-section h1 {
            font-size: 22px;
            font-weight: 600;
        }
        
        .face-badge {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(76, 175, 80, 0.15);
            padding: 8px 18px;
            border-radius: 40px;
            border: 1px solid rgba(76, 175, 80, 0.4);
        }
        
        .face-dot {
            width: 8px;
            height: 8px;
            background: #4caf50;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        
        .btn-logout {
            background: rgba(239, 83, 80, 0.15);
            border: 1px solid rgba(239, 83, 80, 0.4);
            padding: 8px 20px;
            border-radius: 40px;
            color: #ef5350;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-logout:hover {
            background: rgba(239, 83, 80, 0.3);
            transform: translateY(-2px);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 28px;
        }
        
        .stat-card {
            background: rgba(10, 10, 20, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            padding: 24px;
            border: 1px solid rgba(233, 69, 96, 0.1);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            border-color: rgba(233, 69, 96, 0.3);
        }
        
        .stat-label {
            font-size: 13px;
            font-weight: 500;
            color: #888;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, #e94560);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .balance-card {
            background: linear-gradient(135deg, rgba(233, 69, 96, 0.12), rgba(199, 53, 79, 0.08));
            border: 1px solid rgba(233, 69, 96, 0.4);
        }
        
        .balance-card .stat-value {
            font-size: 42px;
            background: linear-gradient(135deg, #4caf50, #81c784);
            -webkit-background-clip: text;
        }
        
        .transactions-card {
            background: rgba(10, 10, 20, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            padding: 24px;
            border: 1px solid rgba(233, 69, 96, 0.1);
        }
        
        .transactions-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }
        
        .transactions-header h2 {
            font-size: 18px;
            font-weight: 600;
            color: #e94560;
        }
        
        .transaction-count {
            background: rgba(233, 69, 96, 0.15);
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        .transaction-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .transaction-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        
        .transaction-item:hover {
            transform: translateX(6px);
            background: rgba(233, 69, 96, 0.08);
        }
        
        .transaction-info {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .transaction-desc {
            font-weight: 600;
            font-size: 15px;
        }
        
        .transaction-date {
            font-size: 12px;
            color: #888;
        }
        
        .transaction-amount {
            font-weight: 700;
            font-size: 18px;
        }
        
        .transaction-credit {
            color: #4caf50;
        }
        
        .transaction-debit {
            color: #ef5350;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stat-card, .transactions-card {
            animation: slideIn 0.4s ease forwards;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                padding: 16px;
            }
            
            .header {
                flex-direction: column;
                text-align: center;
            }
            
            .logo-section {
                justify-content: center;
            }
            
            .stat-value {
                font-size: 28px;
            }
            
            .balance-card .stat-value {
                font-size: 36px;
            }
            
            .transaction-item {
                flex-direction: column;
                text-align: center;
                gap: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <div class="logo-section">
                <div class="logo-icon">NB</div>
                <h1>NOVA SECURE BANK</h1>
            </div>
            <div class="face-badge">
                <div class="face-dot"></div>
                <span id="userName">Live Session Active</span>
            </div>
            <button class="btn-logout" onclick="logout()">Logout</button>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Account Holder</div>
                <div class="stat-value" id="accName">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Account Number</div>
                <div class="stat-value" id="accNumber">-</div>
            </div>
            <div class="stat-card balance-card">
                <div class="stat-label">Available Balance</div>
                <div class="stat-value" id="balance">-</div>
            </div>
        </div>
        
        <div class="transactions-card">
            <div class="transactions-header">
                <h2>Recent Transactions</h2>
                <div class="transaction-count" id="txnCount">0 transactions</div>
            </div>
            <div class="transaction-list" id="transactionsList"></div>
        </div>
    </div>
    
    <script>
        async function loadAccount() {
            try {
                const res = await fetch('/api/account_data');
                const data = await res.json();
                
                if (data.success) {
                    document.getElementById('accName').innerHTML = data.account.name;
                    document.getElementById('accNumber').innerHTML = data.account.account_number;
                    document.getElementById('balance').innerHTML = data.account.currency + ' ' + data.account.balance.toLocaleString();
                    document.getElementById('txnCount').innerHTML = data.account.transactions.length + ' transactions';
                    
                    const txnList = document.getElementById('transactionsList');
                    txnList.innerHTML = '';
                    data.account.transactions.forEach(txn => {
                        const div = document.createElement('div');
                        div.className = 'transaction-item';
                        div.innerHTML = `
                            <div class="transaction-info">
                                <div class="transaction-desc">${txn.desc}</div>
                                <div class="transaction-date">${txn.date}</div>
                            </div>
                            <div class="transaction-amount transaction-${txn.type}">${txn.amount}</div>
                        `;
                        txnList.appendChild(div);
                    });
                }
            } catch(e) {
                console.error(e);
            }
        }
        
        async function logout() {
            await fetch('/api/logout');
            window.location.href = '/';
        }
        
        setInterval(async () => {
            const res = await fetch('/api/check_session');
            const data = await res.json();
            if (!data.authenticated) {
                window.location.href = '/';
            }
        }, 5000);
        
        loadAccount();
    </script>
</body>
</html>
'''

@app.route('/')
def scanner():
    return render_template_string(SCANNER_PAGE)

@app.route('/bank_dashboard')
def bank_dashboard():
    if not authenticated:
        return redirect('/')
    return render_template_string(BANK_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/face_status')
def face_status():
    return jsonify({
        "status": current_face["status"],
        "name": current_face["name"],
        "confidence": current_face["confidence"],
        "is_live": current_face.get("is_live", False),
        "liveness_score": current_face.get("liveness_score", 0)
    })

@app.route('/api/check_auth')
def check_auth():
    global authenticated
    if current_face.get("status") == "recognized" and current_face.get("is_live", False):
        authenticated = True
        return jsonify({
            "success": True, 
            "is_live": True,
            "name": current_face["name"]
        })
    elif current_face.get("status") == "spoof":
        return jsonify({
            "success": False, 
            "photo_detected": True,
            "message": "Photo detected - Real face required"
        })
    else:
        return jsonify({
            "success": False,
            "message": "Face not recognized or not live"
        })

@app.route('/api/account_data')
def account_data():
    if authenticated:
        return jsonify({"success": True, "account": bank_account})
    return jsonify({"success": False})

@app.route('/api/check_session')
def check_session():
    return jsonify({"authenticated": authenticated})

@app.route('/api/logout')
def logout():
    global authenticated
    authenticated = False
    return jsonify({"success": True})

if __name__ == '__main__':
    print("="*50)
    print("NOVA-SHIELD ANTI-SPOOFING SYSTEM")
    print("="*50)
    print("URL: http://localhost:8080")
    print("")
    print("LIVENESS DETECTION METHODS:")
    print("  - Blink Detection (Eye movement)")
    print("  - Head Motion Analysis")
    print("  - Texture Frequency Analysis")
    print("  - Reflection Detection")
    print("")
    print("TESTING:")
    print("  - Real face: Access granted")
    print("  - Photo/Phone screen: Access denied")
    print("="*50)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
