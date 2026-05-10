#!/usr/bin/env python3
"""High Security NOVA-SHIELD with Anti-Spoofing and Bank Demo"""

from flask import Flask, Response, render_template_string, jsonify, session
import cv2
import face_recognition
import pickle
import numpy as np
from pathlib import Path
import time
import json
from datetime import datetime
import os
import base64

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

camera = cv2.VideoCapture(0)

# Anti-spoofing state
blink_history = []
motion_history = []
last_face_position = None
spoof_attempts = 0

# Bank account demo data
bank_accounts = {
    "default": {
        "account_name": "David Kimathi",
        "account_number": "****1234",
        "balance": 15420.50,
        "currency": "KES"
    }
}

def detect_blink(landmarks):
    """Detect eye blink using eye aspect ratio"""
    if 'left_eye' not in landmarks or 'right_eye' not in landmarks:
        return False
    
    def eye_aspect_ratio(eye):
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        ear = (A + B) / (2.0 * C)
        return ear
    
    left_ear = eye_aspect_ratio(np.array(landmarks['left_eye']))
    right_ear = eye_aspect_ratio(np.array(landmarks['right_eye']))
    ear = (left_ear + right_ear) / 2.0
    
    blink_history.append(ear < 0.25)
    if len(blink_history) > 10:
        blink_history.pop(0)
    
    return sum(blink_history) > 0

def detect_motion(face_location):
    """Detect head motion"""
    global last_face_position
    
    if last_face_position is None:
        last_face_position = face_location
        return False
    
    # Calculate movement
    top, right, bottom, left = face_location
    last_top, last_right, last_bottom, last_left = last_face_position
    
    movement = abs(top - last_top) + abs(right - last_right)
    last_face_position = face_location
    
    motion_history.append(movement > 10)
    if len(motion_history) > 5:
        motion_history.pop(0)
    
    return sum(motion_history) > 0

def is_live_face(face_landmarks, face_location):
    """Check if face is live (not a photo/video)"""
    has_blink = detect_blink(face_landmarks)
    has_motion = detect_motion(face_location)
    
    # Require either blink or motion for liveness
    return has_blink or has_motion

def process_frame_for_security(frame):
    """Process frame with anti-spoofing"""
    global spoof_attempts
    
    # Resize for speed
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if not face_locations:
        return frame, {"status": "no_face", "name": None, "confidence": 0}
    
    # Get face landmarks for liveness
    face_landmarks_list = face_recognition.face_landmarks(rgb_frame, face_locations)
    
    # Get face encodings
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    result = {"status": "unknown", "name": None, "confidence": 0, "is_live": False}
    
    for i, (location, encoding, landmarks) in enumerate(zip(face_locations, face_encodings, face_landmarks_list)):
        # Scale back coordinates
        top, right, bottom, left = [int(x * 2) for x in location]
        
        # Check liveness
        live = is_live_face(landmarks, (top, right, bottom, left))
        
        if not live:
            spoof_attempts += 1
            color = (0, 0, 255)  # Red - spoof detected
            label = "SPOOF ATTEMPT DETECTED!"
            result["status"] = "spoof"
        elif known_encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding)
            distances = face_recognition.face_distance(known_encodings, encoding)
            
            if True in matches:
                best_idx = np.argmin(distances)
                confidence = 1 - distances[best_idx]
                
                if confidence > 0.6:
                    color = (0, 255, 0)  # Green - recognized
                    label = f"{known_names[best_idx]} ({confidence*100:.1f}%) [LIVE]"
                    result = {
                        "status": "recognized",
                        "name": known_names[best_idx],
                        "confidence": round(confidence * 100, 1),
                        "is_live": live
                    }
                else:
                    color = (0, 165, 255)  # Orange - low confidence
                    label = "LOW CONFIDENCE"
                    result["status"] = "low_confidence"
            else:
                color = (0, 0, 255)  # Red - unknown
                label = "UNKNOWN FACE"
                result["status"] = "unknown"
        else:
            color = (0, 0, 255)
            label = "NO REGISTERED FACE"
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(frame, (left, bottom - 25), (left + label_size[0], bottom), color, -1)
        cv2.putText(frame, label, (left, bottom - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add spoof warning
        if not live and known_encodings:
            cv2.putText(frame, "[WARNING] PHOTO DETECTED!", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    return frame, result

def generate_video():
    """Generate video feed with face detection and anti-spoofing"""
    frame_skip = 0
    
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        # Process every 3rd frame for performance
        frame_skip += 1
        if frame_skip % 3 == 0:
            processed_frame, result = process_frame_for_security(frame)
        else:
            processed_frame = frame
            result = {"status": "processing"}
        
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        # Store result for status endpoint
        global current_result
        current_result = result

current_result = {"status": "scanning", "name": None, "confidence": 0}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def api_status():
    return jsonify(current_result)

@app.route('/api/bank_account')
def bank_account():
    """Return bank account info if face recognized"""
    if current_result.get("status") == "recognized" and current_result.get("is_live", False):
        account = bank_accounts["default"]
        return jsonify({
            "authenticated": True,
            "account": account,
            "message": "Access granted - Face verified"
        })
    elif current_result.get("status") == "recognized" and not current_result.get("is_live", False):
        return jsonify({
            "authenticated": False,
            "message": "Spoof detected! Photo/Video not allowed"
        })
    else:
        return jsonify({
            "authenticated": False,
            "message": "Please verify your face first"
        })

@app.route('/api/logout')
def logout():
    global current_result
    current_result = {"status": "logged_out", "name": None, "confidence": 0}
    return jsonify({"message": "Logged out successfully"})

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NOVA-SHIELD - High Security Banking</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
        }
        
        /* Left Panel - Camera */
        .camera-panel {
            flex: 1;
            padding: 20px;
            background: linear-gradient(135deg, #0f0f23 0%, #0a0a15 100%);
            border-right: 1px solid #e94560;
        }
        
        .camera-container {
            background: #000;
            border-radius: 15px;
            overflow: hidden;
            border: 2px solid #e94560;
            box-shadow: 0 10px 40px rgba(233, 69, 96, 0.3);
        }
        
        .video-feed {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .security-status {
            margin-top: 20px;
            padding: 15px;
            background: rgba(15, 52, 96, 0.5);
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .status-green { background: #2e7d32; color: #a5d6a7; }
        .status-red { background: #c62828; color: #ef9a9a; }
        .status-yellow { background: #ff8f00; color: #fff3e0; }
        .status-blue { background: #1565c0; color: #90caf9; }
        
        /* Right Panel - Banking Demo */
        .bank-panel {
            flex: 1;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .bank-card {
            background: linear-gradient(135deg, #1a1a3e 0%, #0f0f2a 100%);
            border-radius: 20px;
            padding: 40px;
            border: 1px solid #e94560;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        
        .bank-header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #e94560;
            padding-bottom: 20px;
        }
        
        .bank-header h1 {
            color: #e94560;
            font-size: 32px;
        }
        
        .bank-header p {
            color: #888;
            margin-top: 10px;
        }
        
        .account-details {
            margin: 30px 0;
        }
        
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 15px;
            border-bottom: 1px solid #333;
        }
        
        .detail-label {
            color: #888;
            font-weight: bold;
        }
        
        .detail-value {
            color: #e94560;
            font-size: 20px;
            font-weight: bold;
        }
        
        .balance {
            font-size: 36px;
            color: #4caf50;
        }
        
        .lock-icon {
            font-size: 48px;
            text-align: center;
            margin: 20px 0;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            margin-top: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #e94560;
            color: white;
        }
        
        .btn-primary:hover {
            background: #c7354f;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #333;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #444;
        }
        
        .message-area {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            text-align: center;
        }
        
        .message-success {
            color: #4caf50;
            border-left: 3px solid #4caf50;
        }
        
        .message-error {
            color: #ef5350;
            border-left: 3px solid #ef5350;
        }
        
        .message-warning {
            color: #ff9800;
            border-left: 3px solid #ff9800;
        }
        
        .spoof-alert {
            background: rgba(198, 40, 40, 0.3);
            border: 1px solid #c62828;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        @keyframes glow {
            0% { box-shadow: 0 0 5px #e94560; }
            100% { box-shadow: 0 0 20px #e94560; }
        }
        
        .glow {
            animation: glow 1s ease-in-out infinite alternate;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Left Panel - Camera & Security -->
        <div class="camera-panel">
            <div class="camera-container">
                <img class="video-feed" src="/video_feed" id="videoFeed">
            </div>
            
            <div class="security-status">
                <h3>[SHIELD] Security Status</h3>
                <div id="statusDisplay" style="margin-top: 15px;">
                    <div class="status-badge status-blue">[SCAN] Scanning for face...</div>
                </div>
                <div id="spoofWarning" style="margin-top: 10px;"></div>
                <div style="margin-top: 20px;">
                    <div>[EYE] Blink Detection: Active</div>
                    <div>[MOVE] Motion Analysis: Active</div>
                    <div>[WARN] Anti-Spoof: Enabled</div>
                    <div>[LOCK] Spoof Attempts: <span id="spoofCount">0</span></div>
                </div>
            </div>
        </div>
        
        <!-- Right Panel - Banking Demo -->
        <div class="bank-panel">
            <div class="bank-card" id="bankCard">
                <div class="bank-header">
                    <h1>[BANK] NOVA SECURE BANK</h1>
                    <p>Next-Generation Biometric Banking</p>
                </div>
                
                <div id="authContent">
                    <div class="lock-icon">[LOCK]</div>
                    <div style="text-align: center;">
                        <h3>Face Authentication Required</h3>
                        <p style="color: #888; margin-top: 10px;">Look at the camera to access your account</p>
                        <button class="btn btn-primary" onclick="checkAuth()" style="margin-top: 20px;">[VERIFY] Authenticate</button>
                    </div>
                </div>
                
                <div id="accountContent" style="display: none;">
                    <div class="account-details">
                        <div class="detail-row">
                            <span class="detail-label">[USER] Account Holder</span>
                            <span class="detail-value" id="accName">-</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">[CARD] Account Number</span>
                            <span class="detail-value" id="accNumber">-</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">[MONEY] Available Balance</span>
                            <span class="detail-value balance" id="balance">-</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">[CURRENCY] Currency</span>
                            <span class="detail-value" id="currency">-</span>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-primary" onclick="refreshBalance()">[REFRESH] Refresh Balance</button>
                        <button class="btn btn-secondary" onclick="logout()">[EXIT] Logout</button>
                    </div>
                </div>
                
                <div id="messageArea" class="message-area" style="display: none;"></div>
            </div>
        </div>
    </div>
    
    <script>
        let statusInterval = null;
        
        function showMessage(message, type) {
            const msgDiv = document.getElementById('messageArea');
            msgDiv.innerHTML = message;
            msgDiv.className = 'message-area message-' + type;
            msgDiv.style.display = 'block';
            
            setTimeout(() => {
                msgDiv.style.display = 'none';
            }, 3000);
        }
        
        async function checkAuth() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                const statusDiv = document.getElementById('statusDisplay');
                
                if (data.status === 'spoof') {
                    statusDiv.innerHTML = '<div class="status-badge status-red">[WARN] SPOOF DETECTED - Access Denied</div>';
                    document.getElementById('spoofWarning').innerHTML = '<div class="spoof-alert" style="padding: 10px; border-radius: 5px;">[ALERT] Photo/Video detected! Real face required.</div>';
                    showMessage('[LOCK] Spoof detected! Please use your real face.', 'error');
                    document.getElementById('bankCard').classList.add('spoof-alert');
                    setTimeout(() => document.getElementById('bankCard').classList.remove('spoof-alert'), 2000);
                    return;
                }
                
                if (data.status === 'recognized' && data.is_live) {
                    statusDiv.innerHTML = `<div class="status-badge status-green">[CHECK] FACE VERIFIED - ${data.name} (${data.confidence}%)</div>`;
                    document.getElementById('spoofWarning').innerHTML = '';
                    document.getElementById('bankCard').classList.add('glow');
                    
                    const bankResponse = await fetch('/api/bank_account');
                    const bankData = await bankResponse.json();
                    
                    if (bankData.authenticated) {
                        document.getElementById('authContent').style.display = 'none';
                        document.getElementById('accountContent').style.display = 'block';
                        document.getElementById('accName').innerHTML = bankData.account.account_name;
                        document.getElementById('accNumber').innerHTML = bankData.account.account_number;
                        document.getElementById('balance').innerHTML = bankData.account.balance.toLocaleString();
                        document.getElementById('currency').innerHTML = bankData.account.currency;
                        showMessage('[OK] Access granted! Welcome ' + bankData.account.account_name, 'success');
                        
                        // Add success animation
                        const bankCard = document.getElementById('bankCard');
                        bankCard.style.transform = 'scale(1.02)';
                        setTimeout(() => { bankCard.style.transform = 'scale(1)'; }, 500);
                    }
                } else if (data.status === 'recognized' && !data.is_live) {
                    statusDiv.innerHTML = '<div class="status-badge status-red">[WARN] PHOTO DETECTED - Real face required</div>';
                    showMessage('[WARN] Photo detected! Please use your real face for authentication.', 'warning');
                } else if (data.status === 'no_face') {
                    statusDiv.innerHTML = '<div class="status-badge status-yellow">[CAMERA] No face detected. Look at camera.</div>';
                    showMessage('[CAMERA] No face detected. Please look at the camera.', 'warning');
                } else if (data.status === 'unknown') {
                    statusDiv.innerHTML = '<div class="status-badge status-red">[WARN] Unknown face detected</div>';
                    showMessage('[WARN] Unknown face. Access denied.', 'error');
                } else {
                    statusDiv.innerHTML = '<div class="status-badge status-blue">[SCAN] Scanning for face...</div>';
                }
            } catch(e) {
                console.error(e);
                showMessage('[ERROR] Connection error', 'error');
            }
        }
        
        async function refreshBalance() {
            const response = await fetch('/api/bank_account');
            const data = await response.json();
            if (data.authenticated) {
                document.getElementById('balance').innerHTML = data.account.balance.toLocaleString();
                showMessage('[REFRESH] Balance updated', 'success');
            }
        }
        
        async function logout() {
            await fetch('/api/logout');
            document.getElementById('authContent').style.display = 'block';
            document.getElementById('accountContent').style.display = 'none';
            document.getElementById('messageArea').style.display = 'none';
            document.getElementById('bankCard').classList.remove('glow');
            showMessage('[EXIT] Logged out successfully', 'success');
        }
        
        // Auto-check status every 2 seconds
        setInterval(checkAuth, 2000);
        
        // Initial check
        setTimeout(checkAuth, 1000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("="*50)
    print("NOVA-SHIELD HIGH SECURITY SYSTEM")
    print("="*50)
    print("[INFO] Anti-spoofing: ENABLED")
    print("[INFO] Blink detection: ACTIVE")
    print("[INFO] Motion analysis: ACTIVE")
    print("[INFO] Banking demo: READY")
    print("")
    print("[URL] Open: http://localhost:8080")
    print("[TEST] Try using a photo of yourself - it will be rejected")
    print("="*50)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
