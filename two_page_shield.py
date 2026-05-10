#!/usr/bin/env python3
"""Two-Page NOVA-SHIELD: Face Scan -> Bank Dashboard"""

from flask import Flask, Response, render_template_string, jsonify, session, redirect, url_for
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

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Session state
authenticated = False
current_face = {"status": "scanning", "name": None, "confidence": 0}

# Bank data
bank_account = {
    "name": "DAVID KIMATHI",
    "account_number": "01-234-5678",
    "balance": 15420.50,
    "currency": "KES",
    "transactions": [
        {"date": "2024-05-10", "desc": "Salary Deposit", "amount": "+45,000", "type": "credit"},
        {"date": "2024-05-09", "desc": "Online Payment", "amount": "-2,500", "type": "debit"},
        {"date": "2024-05-08", "desc": "ATM Withdrawal", "amount": "-10,000", "type": "debit"},
        {"date": "2024-05-07", "desc": "Mobile Recharge", "amount": "-500", "type": "debit"},
        {"date": "2024-05-05", "desc": "Interest Credit", "amount": "+1,200", "type": "credit"},
    ]
}

def detect_face(frame):
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
        
        # Add scan message
        if current_face["status"] == "recognized":
            cv2.putText(processed, "FACE VERIFIED", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        elif current_face["status"] == "unknown":
            cv2.putText(processed, "UNKNOWN FACE", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(processed, "SCANNING...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
        
        ret, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 75])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Page 1: Face Scanner
SCANNER_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NOVA-SHIELD - Face Scanner</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .scanner-container {
            max-width: 500px;
            width: 100%;
            padding: 20px;
        }
        .scanner-card {
            background: rgba(15, 52, 96, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid #e94560;
            text-align: center;
        }
        .scanner-card h1 {
            color: #e94560;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .scanner-card p {
            color: #888;
            margin-bottom: 20px;
        }
        .video-box {
            background: #000;
            border-radius: 15px;
            overflow: hidden;
            border: 2px solid #e94560;
            margin-bottom: 20px;
        }
        .video-feed {
            width: 100%;
            display: block;
        }
        .status-area {
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
        }
        .status-scanning {
            background: #1565c0;
            color: #90caf9;
        }
        .status-success {
            background: #2e7d32;
            color: #a5d6a7;
        }
        .status-failed {
            background: #c62828;
            color: #ef9a9a;
        }
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #333;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 20px;
        }
        .progress-fill {
            width: 0%;
            height: 100%;
            background: #e94560;
            transition: width 0.1s linear;
        }
        .btn {
            width: 100%;
            padding: 12px;
            margin-top: 15px;
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
    <div class="scanner-container">
        <div class="scanner-card">
            <h1>[SCAN] FACE SCANNER</h1>
            <p>Please look at the camera for verification</p>
            
            <div class="video-box">
                <img class="video-feed" src="/video_feed" id="videoFeed">
            </div>
            
            <div id="statusArea" class="status-area status-scanning pulse">
                [SCAN] Scanning for face...
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            
            <div id="actionArea">
                <button class="btn btn-primary" onclick="checkAuth()" id="authBtn">
                    [VERIFY] Verify Identity
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let checkInterval = null;
        let progress = 0;
        
        async function checkAuth() {
            const statusDiv = document.getElementById('statusArea');
            const authBtn = document.getElementById('authBtn');
            
            authBtn.disabled = true;
            authBtn.innerHTML = '[WAIT] Verifying...';
            
            try {
                const res = await fetch('/api/check_auth');
                const data = await res.json();
                
                if (data.success) {
                    statusDiv.className = 'status-area status-success';
                    statusDiv.innerHTML = `[SUCCESS] Welcome ${data.name}! Redirecting...`;
                    
                    // Redirect to bank dashboard
                    setTimeout(() => {
                        window.location.href = '/bank_dashboard';
                    }, 1500);
                } else {
                    statusDiv.className = 'status-area status-failed';
                    statusDiv.innerHTML = `[FAIL] ${data.message}`;
                    authBtn.disabled = false;
                    authBtn.innerHTML = '[RETRY] Try Again';
                    
                    setTimeout(() => {
                        statusDiv.className = 'status-area status-scanning';
                        statusDiv.innerHTML = '[SCAN] Scanning for face...';
                    }, 2000);
                }
            } catch(e) {
                statusDiv.className = 'status-area status-failed';
                statusDiv.innerHTML = '[ERROR] Connection failed';
                authBtn.disabled = false;
                authBtn.innerHTML = '[RETRY] Try Again';
            }
        }
        
        // Auto-check face every second
        setInterval(async () => {
            try {
                const res = await fetch('/api/face_status');
                const data = await res.json();
                const statusDiv = document.getElementById('statusArea');
                const progressFill = document.getElementById('progressFill');
                
                if (data.status === 'recognized') {
                    statusDiv.className = 'status-area status-success';
                    statusDiv.innerHTML = `[OK] Face Detected: ${data.name} (${data.confidence}%)`;
                    progress = Math.min(progress + 10, 100);
                    progressFill.style.width = progress + '%';
                    
                    if (progress >= 100) {
                        checkAuth();
                    }
                } else if (data.status === 'unknown') {
                    statusDiv.className = 'status-area status-failed';
                    statusDiv.innerHTML = '[WARN] Unknown face detected';
                    progress = 0;
                    progressFill.style.width = '0%';
                } else {
                    statusDiv.className = 'status-area status-scanning';
                    statusDiv.innerHTML = '[SCAN] Looking for face...';
                    progress = 0;
                    progressFill.style.width = '0%';
                }
            } catch(e) {}
        }, 500);
    </script>
</body>
</html>
'''

# Page 2: Bank Dashboard
BANK_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NOVA-SHIELD - Bank Dashboard</title>
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
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
        }
        /* Header */
        .header {
            background: rgba(15, 52, 96, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e94560;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #e94560;
            font-size: 28px;
        }
        .user-badge {
            background: #2e7d32;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
        }
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(15, 52, 96, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #0f3460;
            text-align: center;
        }
        .stat-card h3 {
            color: #888;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #e94560;
        }
        .balance-card {
            background: linear-gradient(135deg, #1a1a3e 0%, #0f0f2a 100%);
            border: 2px solid #e94560;
        }
        .balance-card .value {
            font-size: 48px;
            color: #4caf50;
        }
        /* Transactions */
        .transactions-card {
            background: rgba(15, 52, 96, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #0f3460;
        }
        .transactions-card h2 {
            color: #e94560;
            margin-bottom: 20px;
            font-size: 20px;
        }
        .transaction-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #333;
        }
        .transaction-item:last-child {
            border-bottom: none;
        }
        .transaction-date {
            color: #888;
            font-size: 12px;
        }
        .transaction-desc {
            font-weight: bold;
        }
        .transaction-credit {
            color: #4caf50;
        }
        .transaction-debit {
            color: #ef5350;
        }
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-danger {
            background: #c62828;
            color: white;
        }
        .btn-danger:hover {
            background: #b71c1c;
        }
        .face-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .face-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        .dot-green {
            background: #4caf50;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>[BANK] NOVA SECURE BANK</h1>
            <div class="face-indicator">
                <div class="face-dot dot-green"></div>
                <span id="userName">Loading...</span>
                <button class="btn btn-danger" onclick="logout()">[EXIT] Logout</button>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>[USER] Account Holder</h3>
                <div class="value" id="accName">-</div>
            </div>
            <div class="stat-card">
                <h3>[CARD] Account Number</h3>
                <div class="value" id="accNumber">-</div>
            </div>
            <div class="stat-card balance-card">
                <h3>[MONEY] Available Balance</h3>
                <div class="value" id="balance">-</div>
            </div>
        </div>
        
        <div class="transactions-card">
            <h2>[HISTORY] Recent Transactions</h2>
            <div id="transactionsList"></div>
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
                    document.getElementById('balance').innerHTML = `${data.account.currency} ${data.account.balance.toLocaleString()}`;
                    document.getElementById('userName').innerHTML = `[FACE] ${data.account.name}`;
                    
                    // Load transactions
                    const txnList = document.getElementById('transactionsList');
                    txnList.innerHTML = '';
                    data.account.transactions.forEach(txn => {
                        const div = document.createElement('div');
                        div.className = 'transaction-item';
                        div.innerHTML = `
                            <div>
                                <div class="transaction-desc">${txn.desc}</div>
                                <div class="transaction-date">${txn.date}</div>
                            </div>
                            <div class="transaction-${txn.type}">${txn.amount}</div>
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
        
        // Keep session alive with periodic check
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
        "confidence": current_face["confidence"]
    })

@app.route('/api/check_auth')
def check_auth():
    global authenticated
    if current_face["status"] == "recognized" and current_face["confidence"] > 55:
        authenticated = True
        return jsonify({
            "success": True,
            "name": current_face["name"]
        })
    else:
        return jsonify({
            "success": False,
            "message": "Face not recognized. Please look at camera."
        })

@app.route('/api/account_data')
def account_data():
    if authenticated:
        return jsonify({
            "success": True,
            "account": bank_account
        })
    else:
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
    print("NOVA-SHIELD TWO-PAGE BANKING SYSTEM")
    print("="*50)
    print("[PAGE 1] Face Scanner - http://localhost:8080")
    print("[PAGE 2] Bank Dashboard - Shows after face verification")
    print("="*50)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
