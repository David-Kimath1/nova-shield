#!/usr/bin/env python3
"""Premium NOVA-SHIELD with Modern UI/UX"""

from flask import Flask, Response, render_template_string, jsonify, session, redirect
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

authenticated = False
current_face = {"status": "scanning", "name": None, "confidence": 0}

bank_account = {
    "name": "DAVID KIMATHI",
    "account_number": "01-234-5678",
    "balance": 15420.50,
    "currency": "KES",
    "transactions": [
        {"date": "2024-05-10", "desc": "Salary Deposit", "amount": "+45,000", "type": "credit"},
        {"date": "2024-05-09", "desc": "Online Payment - Amazon", "amount": "-2,500", "type": "debit"},
        {"date": "2024-05-08", "desc": "ATM Withdrawal", "amount": "-10,000", "type": "debit"},
        {"date": "2024-05-07", "desc": "Mobile Recharge - Safaricom", "amount": "-500", "type": "debit"},
        {"date": "2024-05-05", "desc": "Interest Credit", "amount": "+1,200", "type": "credit"},
        {"date": "2024-05-03", "desc": "Netflix Subscription", "amount": "-1,200", "type": "debit"},
        {"date": "2024-05-01", "desc": "Freelance Payment", "amount": "+25,000", "type": "credit"},
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
                label = f"{known_names[best_idx]}"
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
        ret, buffer = cv2.imencode('.jpg', processed, [cv2.IMWRITE_JPEG_QUALITY, 75])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Modern Scanner Page
SCANNER_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>NOVA-SHIELD | Face Authentication</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: radial-gradient(ellipse at 20% 30%, #0a0a0a, #000000);
            min-height: 100vh;
            color: #ffffff;
            overflow-x: hidden;
        }
        
        /* Animated Background */
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
        
        /* Main Container */
        .container {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        /* Scanner Card */
        .scanner-card {
            max-width: 500px;
            width: 100%;
            background: rgba(10, 10, 20, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 48px;
            padding: 32px;
            border: 1px solid rgba(233, 69, 96, 0.2);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease;
        }
        
        .scanner-card:hover {
            transform: translateY(-5px);
        }
        
        /* Logo Section */
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
            font-size: 32px;
            margin-bottom: 16px;
            box-shadow: 0 10px 40px rgba(233, 69, 96, 0.3);
        }
        
        .logo h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e94560);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .logo p {
            color: #888;
            font-size: 14px;
            margin-top: 8px;
        }
        
        /* Video Container */
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
        
        .video-wrapper:hover .video-glow {
            opacity: 0.6;
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
        
        /* Status Section */
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
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        .status-dot.success {
            background: #4caf50;
        }
        
        .status-dot.error {
            background: #ef5350;
        }
        
        .status-text {
            font-size: 16px;
            font-weight: 500;
        }
        
        .confidence-bar {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            height: 8px;
            overflow: hidden;
        }
        
        .confidence-fill {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #e94560, #ff6b8a);
            border-radius: 12px;
            transition: width 0.3s ease;
        }
        
        /* Button */
        .btn-verify {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #e94560, #c7354f);
            border: none;
            border-radius: 40px;
            color: white;
            font-size: 16px;
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
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .scanner-card {
                padding: 20px;
                border-radius: 32px;
            }
            
            .logo-icon {
                width: 48px;
                height: 48px;
                font-size: 24px;
            }
            
            .logo h1 {
                font-size: 24px;
            }
            
            .status-text {
                font-size: 14px;
            }
            
            .btn-verify {
                padding: 14px;
                font-size: 14px;
            }
        }
        
        @media (max-width: 480px) {
            .container {
                padding: 16px;
            }
            
            .scanner-card {
                padding: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    <div class="container">
        <div class="scanner-card">
            <div class="logo">
                <div class="logo-icon">🛡️</div>
                <h1>NOVA-SHIELD</h1>
                <p>Biometric Authentication System</p>
            </div>
            
            <div class="video-wrapper">
                <div class="video-glow"></div>
                <div class="video-box">
                    <img class="video-feed" src="/video_feed" id="videoFeed">
                </div>
            </div>
            
            <div class="status-card">
                <div class="status-header">
                    <div class="status-dot" id="statusDot"></div>
                    <div class="status-text" id="statusText">Initializing camera...</div>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" id="confidenceFill"></div>
                </div>
            </div>
            
            <button class="btn-verify" onclick="verifyFace()" id="verifyBtn">
                <span>🔒</span> Verify Identity
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
                const verifyBtn = document.getElementById('verifyBtn');
                
                if (data.status === 'recognized') {
                    statusDot.className = 'status-dot success';
                    statusText.innerHTML = `✓ Face recognized - ${data.name} (${data.confidence}%)`;
                    confidenceFill.style.width = `${data.confidence}%`;
                    
                    if (!isVerifying && data.confidence > 60) {
                        setTimeout(() => verifyFace(), 500);
                    }
                } else if (data.status === 'unknown') {
                    statusDot.className = 'status-dot error';
                    statusText.innerHTML = '⚠ Unknown face detected';
                    confidenceFill.style.width = '0%';
                } else {
                    statusDot.className = 'status-dot';
                    statusText.innerHTML = '📷 Looking for face...';
                    confidenceFill.style.width = '0%';
                }
            } catch(e) {
                console.error(e);
            }
        }
        
        async function verifyFace() {
            if (isVerifying) return;
            isVerifying = true;
            const btn = document.getElementById('verifyBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span>⏳</span> Verifying...';
            btn.disabled = true;
            
            try {
                const res = await fetch('/api/check_auth');
                const data = await res.json();
                
                if (data.success) {
                    btn.innerHTML = '<span>✓</span> Success! Redirecting...';
                    setTimeout(() => {
                        window.location.href = '/bank_dashboard';
                    }, 1000);
                } else {
                    btn.innerHTML = '<span>❌</span> Try Again';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                        isVerifying = false;
                    }, 2000);
                }
            } catch(e) {
                btn.innerHTML = '<span>⚠</span> Error';
                setTimeout(() => {
                    btn.innerHTML = originalText;
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

# Modern Bank Dashboard Page
BANK_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>NOVA-SHIELD | Bank Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: radial-gradient(ellipse at 20% 30%, #0a0a0a, #000000);
            min-height: 100vh;
            color: #ffffff;
        }
        
        /* Dashboard Container */
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }
        
        /* Header */
        .header {
            background: rgba(10, 10, 20, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            padding: 20px 24px;
            margin-bottom: 24px;
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
            font-size: 24px;
        }
        
        .logo-section h1 {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e94560);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .user-section {
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }
        
        .face-badge {
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(76, 175, 80, 0.2);
            padding: 8px 16px;
            border-radius: 40px;
            border: 1px solid rgba(76, 175, 80, 0.5);
        }
        
        .face-dot {
            width: 10px;
            height: 10px;
            background: #4caf50;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        
        .btn-logout {
            background: rgba(239, 83, 80, 0.2);
            border: 1px solid rgba(239, 83, 80, 0.5);
            padding: 10px 20px;
            border-radius: 40px;
            color: #ef5350;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-logout:hover {
            background: rgba(239, 83, 80, 0.4);
            transform: translateY(-2px);
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }
        
        .stat-card {
            background: rgba(10, 10, 20, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            padding: 24px;
            border: 1px solid rgba(233, 69, 96, 0.1);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: rgba(233, 69, 96, 0.3);
        }
        
        .stat-label {
            font-size: 14px;
            color: #888;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .stat-value {
            font-size: 36px;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, #e94560);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .balance-card {
            background: linear-gradient(135deg, rgba(233, 69, 96, 0.15), rgba(199, 53, 79, 0.1));
            border: 1px solid rgba(233, 69, 96, 0.5);
        }
        
        .balance-card .stat-value {
            font-size: 48px;
            background: linear-gradient(135deg, #4caf50, #81c784);
            -webkit-background-clip: text;
        }
        
        /* Transactions */
        .transactions-card {
            background: rgba(10, 10, 20, 0.6);
            backdrop-filter: blur(20px);
            border-radius: 32px;
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
            font-size: 20px;
            font-weight: 600;
            color: #e94560;
        }
        
        .transaction-count {
            background: rgba(233, 69, 96, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        .transaction-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .transaction-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .transaction-item:hover {
            transform: translateX(5px);
            background: rgba(233, 69, 96, 0.1);
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
        
        /* Mobile Responsive */
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
            
            .user-section {
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
        
        @media (max-width: 480px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .stat-card {
                padding: 18px;
            }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Slide In Animation */
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
            animation: slideIn 0.5s ease forwards;
        }
        
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .transactions-card { animation-delay: 0.4s; }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <div class="logo-section">
                <div class="logo-icon">🏦</div>
                <h1>NOVA SECURE BANK</h1>
            </div>
            <div class="user-section">
                <div class="face-badge">
                    <div class="face-dot"></div>
                    <span id="userName">Loading...</span>
                </div>
                <button class="btn-logout" onclick="logout()">
                    🔒 Logout
                </button>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">
                    <span>👤</span> Account Holder
                </div>
                <div class="stat-value" id="accName">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">
                    <span>💳</span> Account Number
                </div>
                <div class="stat-value" id="accNumber">-</div>
            </div>
            <div class="stat-card balance-card">
                <div class="stat-label">
                    <span>💰</span> Available Balance
                </div>
                <div class="stat-value" id="balance">-</div>
            </div>
        </div>
        
        <div class="transactions-card">
            <div class="transactions-header">
                <h2>📊 Recent Transactions</h2>
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
                    document.getElementById('balance').innerHTML = `${data.account.currency} ${data.account.balance.toLocaleString()}`;
                    document.getElementById('userName').innerHTML = `✓ ${data.account.name}`;
                    document.getElementById('txnCount').innerHTML = `${data.account.transactions.length} transactions`;
                    
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
        "confidence": current_face["confidence"]
    })

@app.route('/api/check_auth')
def check_auth():
    global authenticated
    if current_face["status"] == "recognized" and current_face["confidence"] > 55:
        authenticated = True
        return jsonify({"success": True, "name": current_face["name"]})
    return jsonify({"success": False, "message": "Face not recognized"})

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
    print("NOVA-SHIELD PREMIUM UI SYSTEM")
    print("="*50)
    print("[URL] http://localhost:8080")
    print("[DESIGN] Modern glassmorphism + smooth animations")
    print("[RESPONSIVE] Mobile, tablet, desktop ready")
    print("="*50)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
