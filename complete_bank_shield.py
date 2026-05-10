#!/usr/bin/env python3
"""Complete NOVA-SHIELD with Bank Authentication"""

from flask import Flask, Response, render_template_string, jsonify, session
import cv2
import face_recognition
import pickle
import numpy as np
from pathlib import Path
import time
import json
import os

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
else:
    print("[ERROR] No face registered. Run: python3 register_first_face.py")

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Global variables
current_face = {"status": "scanning", "name": None, "confidence": 0, "authenticated": False}
last_auth_time = 0

# Bank data
bank_account = {
    "name": "DAVID KIMATHI",
    "account_number": "01-234-5678",
    "balance": 15420.50,
    "currency": "KES",
    "last_login": None
}

def authenticate_face():
    """Check if current face is authenticated"""
    global last_auth_time
    
    if current_face["status"] == "recognized" and current_face["confidence"] > 60:
        current_face["authenticated"] = True
        last_auth_time = time.time()
        return True
    else:
        # Auto-logout after 10 seconds of no face
        if time.time() - last_auth_time > 10:
            current_face["authenticated"] = False
        return current_face["authenticated"]

def detect_face(frame):
    """Detect and recognize face"""
    global current_face
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb, model="hog")
    
    if not face_locations:
        current_face["status"] = "no_face"
        return frame
    
    face_encodings = face_recognition.face_encodings(rgb, face_locations)
    
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        if known_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_idx = np.argmin(distances)
            confidence = 1 - distances[best_idx]
            
            if confidence > 0.55:
                current_face = {
                    "status": "recognized",
                    "name": known_names[best_idx],
                    "confidence": round(confidence * 100, 1),
                    "authenticated": current_face.get("authenticated", False)
                }
                color = (0, 255, 0)
                label = f"{known_names[best_idx]} ({confidence*100:.0f}%)"
            else:
                current_face = {
                    "status": "unknown",
                    "name": None,
                    "confidence": 0,
                    "authenticated": False
                }
                color = (0, 0, 255)
                label = "UNKNOWN"
        else:
            color = (0, 0, 255)
            label = "NO REGISTERED FACE"
        
        # Draw box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw auth status
        if current_face.get("authenticated", False):
            cv2.putText(frame, "AUTHENTICATED", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return frame

def generate_video():
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        processed = detect_face(frame)
        authenticate_face()  # Update auth status
        
        ret, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 75])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": current_face["status"],
        "name": current_face["name"],
        "confidence": current_face["confidence"],
        "authenticated": current_face.get("authenticated", False)
    })

@app.route('/api/auth')
def api_auth():
    """Force authentication check"""
    authenticated = authenticate_face()
    if authenticated and current_face["status"] == "recognized":
        bank_account["last_login"] = time.strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({
            "success": True,
            "message": f"Welcome {current_face['name']}!",
            "account": bank_account
        })
    else:
        return jsonify({
            "success": False,
            "message": "Face not recognized. Please look at camera."
        })

@app.route('/api/logout')
def api_logout():
    current_face["authenticated"] = False
    return jsonify({"success": True, "message": "Logged out"})

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>NOVA-SHIELD - Secure Banking</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            font-family: 'Segoe UI', monospace;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        /* Camera Panel */
        .camera-panel {
            background: rgba(15, 52, 96, 0.3);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid #e94560;
        }
        .camera-panel h2 {
            color: #e94560;
            margin-bottom: 15px;
        }
        .video-container {
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #e94560;
        }
        .video-feed {
            width: 100%;
            display: block;
        }
        .status-box {
            margin-top: 15px;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        }
        .status-green {
            background: #2e7d32;
            color: #a5d6a7;
        }
        .status-red {
            background: #c62828;
            color: #ef9a9a;
        }
        .status-yellow {
            background: #ff8f00;
            color: #fff3e0;
        }
        .status-blue {
            background: #1565c0;
            color: #90caf9;
        }
        /* Bank Panel */
        .bank-panel {
            background: linear-gradient(135deg, #0f0f23 0%, #0a0a15 100%);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid #e94560;
        }
        .bank-header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #e94560;
            padding-bottom: 20px;
        }
        .bank-header h1 {
            color: #e94560;
            font-size: 28px;
        }
        .bank-header p {
            color: #888;
            margin-top: 5px;
        }
        .account-card {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            border-bottom: 1px solid #333;
        }
        .detail-label {
            color: #888;
            font-weight: bold;
        }
        .detail-value {
            color: #e94560;
            font-weight: bold;
            font-size: 18px;
        }
        .balance {
            font-size: 32px;
            color: #4caf50;
        }
        .btn {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
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
        .message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-size: 14px;
        }
        .message-success {
            background: #2e7d3220;
            color: #4caf50;
            border: 1px solid #2e7d32;
        }
        .message-error {
            background: #c6282820;
            color: #ef5350;
            border: 1px solid #c62828;
        }
        .locked {
            text-align: center;
            padding: 40px;
        }
        .locked-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .pulse {
            animation: pulse 1.5s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Camera Panel -->
        <div class="camera-panel">
            <h2>[CAMERA] Face Verification</h2>
            <div class="video-container">
                <img class="video-feed" src="/video_feed" id="videoFeed">
            </div>
            <div id="cameraStatus" class="status-box status-blue pulse">
                [WAIT] Looking for face...
            </div>
            <div style="margin-top: 15px; font-size: 12px; color: #888; text-align: center;">
                [INFO] Look directly at camera | Green box = Face detected
            </div>
        </div>
        
        <!-- Bank Panel -->
        <div class="bank-panel" id="bankPanel">
            <div class="bank-header">
                <h1>[BANK] NOVA SECURE BANK</h1>
                <p>Biometric Authentication System</p>
            </div>
            
            <div id="loginView">
                <div class="locked">
                    <div class="locked-icon">[LOCK]</div>
                    <h3>Account Locked</h3>
                    <p style="color: #888; margin: 10px 0;">Face authentication required</p>
                    <button class="btn btn-primary" onclick="authenticate()" id="authBtn">
                        [VERIFY] Authenticate with Face
                    </button>
                </div>
            </div>
            
            <div id="accountView" style="display: none;">
                <div class="account-card">
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
                        <span class="detail-label">[TIME] Last Login</span>
                        <span class="detail-value" id="lastLogin">-</span>
                    </div>
                </div>
                
                <button class="btn btn-secondary" onclick="logout()">
                    [EXIT] Logout & Lock Account
                </button>
            </div>
            
            <div id="messageDiv" class="message" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        let autoAuthInterval = null;
        
        // Update camera status every second
        setInterval(async () => {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                const statusDiv = document.getElementById('cameraStatus');
                
                if (data.status === 'recognized') {
                    statusDiv.className = 'status-box status-green';
                    statusDiv.innerHTML = `[OK] FACE RECOGNIZED - ${data.name} (${data.confidence}%)`;
                    
                    // Auto-authenticate if not already
                    const accountView = document.getElementById('accountView');
                    if (accountView.style.display === 'none') {
                        authenticate();
                    }
                } else if (data.status === 'unknown') {
                    statusDiv.className = 'status-box status-red';
                    statusDiv.innerHTML = '[WARN] UNKNOWN FACE DETECTED';
                } else if (data.status === 'no_face') {
                    statusDiv.className = 'status-box status-yellow';
                    statusDiv.innerHTML = '[CAMERA] NO FACE DETECTED';
                } else {
                    statusDiv.className = 'status-box status-blue';
                    statusDiv.innerHTML = '[SCAN] Scanning for face...';
                }
            } catch(e) {
                console.error(e);
            }
        }, 1000);
        
        async function authenticate() {
            const messageDiv = document.getElementById('messageDiv');
            const authBtn = document.getElementById('authBtn');
            
            if (authBtn) {
                authBtn.disabled = true;
                authBtn.innerHTML = '[WAIT] Verifying...';
            }
            
            try {
                const res = await fetch('/api/auth');
                const data = await res.json();
                
                if (data.success) {
                    messageDiv.className = 'message message-success';
                    messageDiv.innerHTML = `[SUCCESS] ${data.message}`;
                    messageDiv.style.display = 'block';
                    
                    // Show account
                    document.getElementById('loginView').style.display = 'none';
                    document.getElementById('accountView').style.display = 'block';
                    
                    // Fill account details
                    document.getElementById('accName').innerHTML = data.account.name;
                    document.getElementById('accNumber').innerHTML = data.account.account_number;
                    document.getElementById('balance').innerHTML = `${data.account.currency} ${data.account.balance.toLocaleString()}`;
                    document.getElementById('lastLogin').innerHTML = data.account.last_login || 'Just now';
                    
                    setTimeout(() => {
                        messageDiv.style.display = 'none';
                    }, 3000);
                } else {
                    messageDiv.className = 'message message-error';
                    messageDiv.innerHTML = `[FAIL] ${data.message}`;
                    messageDiv.style.display = 'block';
                    
                    setTimeout(() => {
                        messageDiv.style.display = 'none';
                    }, 3000);
                }
            } catch(e) {
                messageDiv.className = 'message message-error';
                messageDiv.innerHTML = '[ERROR] Connection failed';
                messageDiv.style.display = 'block';
            }
            
            if (authBtn) {
                authBtn.disabled = false;
                authBtn.innerHTML = '[VERIFY] Authenticate with Face';
            }
        }
        
        async function logout() {
            await fetch('/api/logout');
            
            document.getElementById('loginView').style.display = 'block';
            document.getElementById('accountView').style.display = 'none';
            
            const messageDiv = document.getElementById('messageDiv');
            messageDiv.className = 'message message-success';
            messageDiv.innerHTML = '[EXIT] Logged out successfully';
            messageDiv.style.display = 'block';
            
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 2000);
        }
        
        // Auto-check authentication on page load
        setTimeout(() => {
            authenticate();
        }, 2000);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("="*50)
    print("NOVA-SHIELD COMPLETE BANKING SYSTEM")
    print("="*50)
    print("[INFO] Face recognition + Bank authentication")
    print("[INFO] Green box = Face recognized")
    print("[INFO] Click 'Authenticate' or wait for auto-auth")
    print("[URL] http://localhost:8080")
    print("="*50)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
