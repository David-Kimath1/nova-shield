#!/usr/bin/env python3
"""Working NOVA-SHIELD with Bank - Disabled anti-spoofing for now"""

from flask import Flask, Response, render_template_string, jsonify, session
import cv2
import face_recognition
import pickle
import numpy as np
from pathlib import Path
import time
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
    print("[ERROR] Run: python3 register_first_face.py")

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# State
current_face = {"status": "scanning", "name": None, "confidence": 0}
authenticated = False
bank_account = {
    "name": "DAVID KIMATHI",
    "account_number": "01-234-5678",
    "balance": 15420.50,
    "currency": "KES"
}

def detect_face(frame):
    """Simple face detection - no anti-spoofing"""
    global current_face
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb, model="hog")
    
    if not face_locations:
        current_face = {"status": "no_face", "name": None, "confidence": 0}
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
                    "confidence": round(confidence * 100, 1)
                }
                color = (0, 255, 0)
                label = f"{known_names[best_idx]} ({confidence*100:.0f}%)"
            else:
                current_face = {"status": "unknown", "name": None, "confidence": 0}
                color = (0, 0, 255)
                label = "UNKNOWN"
        else:
            color = (0, 0, 255)
            label = "NO REGISTERED FACE"
        
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return frame

def generate_video():
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        processed = detect_face(frame)
        
        if authenticated:
            cv2.putText(processed, "AUTHENTICATED", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
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
        "authenticated": authenticated
    })

@app.route('/api/auth')
def api_auth():
    global authenticated
    if current_face["status"] == "recognized" and current_face["confidence"] > 55:
        authenticated = True
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
    global authenticated
    authenticated = False
    return jsonify({"success": True})

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
        .status-green { background: #2e7d32; color: #a5d6a7; }
        .status-red { background: #c62828; color: #ef9a9a; }
        .status-yellow { background: #ff8f00; color: #fff3e0; }
        .status-blue { background: #1565c0; color: #90caf9; }
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
        .bank-header h1 { color: #e94560; font-size: 28px; }
        .bank-header p { color: #888; margin-top: 5px; }
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
        .detail-label { color: #888; font-weight: bold; }
        .detail-value { color: #e94560; font-weight: bold; font-size: 18px; }
        .balance { font-size: 32px; color: #4caf50; }
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
        .btn-primary { background: #e94560; color: white; }
        .btn-primary:hover { background: #c7354f; transform: translateY(-2px); }
        .btn-secondary { background: #333; color: white; }
        .btn-secondary:hover { background: #444; }
        .message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .message-success { background: #2e7d3220; color: #4caf50; border: 1px solid #2e7d32; }
        .message-error { background: #c6282820; color: #ef5350; border: 1px solid #c62828; }
        .locked { text-align: center; padding: 40px; }
        .locked-icon { font-size: 64px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="camera-panel">
            <h2>[CAMERA] Face Verification</h2>
            <div class="video-container">
                <img class="video-feed" src="/video_feed">
            </div>
            <div id="cameraStatus" class="status-box status-blue">
                [WAIT] Looking for face...
            </div>
        </div>
        
        <div class="bank-panel">
            <div class="bank-header">
                <h1>[BANK] NOVA SECURE BANK</h1>
                <p>Biometric Authentication System</p>
            </div>
            
            <div id="loginView">
                <div class="locked">
                    <div class="locked-icon">[LOCK]</div>
                    <h3>Account Locked</h3>
                    <p style="color: #888; margin: 10px 0;">Face authentication required</p>
                    <button class="btn btn-primary" onclick="authenticate()">
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
                </div>
                <button class="btn btn-secondary" onclick="logout()">[EXIT] Logout</button>
            </div>
            
            <div id="messageDiv" class="message" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        setInterval(async () => {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                const statusDiv = document.getElementById('cameraStatus');
                
                if (data.status === 'recognized') {
                    statusDiv.className = 'status-box status-green';
                    statusDiv.innerHTML = `[OK] ${data.name} (${data.confidence}%)`;
                } else if (data.status === 'unknown') {
                    statusDiv.className = 'status-box status-red';
                    statusDiv.innerHTML = '[WARN] UNKNOWN FACE';
                } else {
                    statusDiv.className = 'status-box status-yellow';
                    statusDiv.innerHTML = '[CAMERA] No face detected';
                }
                
                // Auto-auth if face recognized
                if (data.status === 'recognized' && document.getElementById('accountView').style.display === 'none') {
                    authenticate();
                }
            } catch(e) {}
        }, 1000);
        
        async function authenticate() {
            const msgDiv = document.getElementById('messageDiv');
            try {
                const res = await fetch('/api/auth');
                const data = await res.json();
                
                if (data.success) {
                    msgDiv.className = 'message message-success';
                    msgDiv.innerHTML = `[SUCCESS] ${data.message}`;
                    msgDiv.style.display = 'block';
                    
                    document.getElementById('loginView').style.display = 'none';
                    document.getElementById('accountView').style.display = 'block';
                    
                    document.getElementById('accName').innerHTML = data.account.name;
                    document.getElementById('accNumber').innerHTML = data.account.account_number;
                    document.getElementById('balance').innerHTML = `${data.account.currency} ${data.account.balance.toLocaleString()}`;
                    
                    setTimeout(() => msgDiv.style.display = 'none', 3000);
                } else {
                    msgDiv.className = 'message message-error';
                    msgDiv.innerHTML = `[FAIL] ${data.message}`;
                    msgDiv.style.display = 'block';
                    setTimeout(() => msgDiv.style.display = 'none', 3000);
                }
            } catch(e) {
                msgDiv.className = 'message message-error';
                msgDiv.innerHTML = '[ERROR] Connection failed';
                msgDiv.style.display = 'block';
            }
        }
        
        async function logout() {
            await fetch('/api/logout');
            document.getElementById('loginView').style.display = 'block';
            document.getElementById('accountView').style.display = 'none';
            
            const msgDiv = document.getElementById('messageDiv');
            msgDiv.className = 'message message-success';
            msgDiv.innerHTML = '[EXIT] Logged out';
            msgDiv.style.display = 'block';
            setTimeout(() => msgDiv.style.display = 'none', 2000);
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("="*50)
    print("NOVA-SHIELD WORKING BANK SYSTEM")
    print("="*50)
    print("[INFO] Anti-spoofing DISABLED for reliability")
    print("[INFO] Face recognition ACTIVE")
    print("[URL] http://localhost:8080")
    print("="*50)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
