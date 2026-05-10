.# NOVA-SHIELD

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://linux.org)
[![Face Recognition](https://img.shields.io/badge/Face%20Recognition-AI-red.svg)](https://github.com/ageitgey/face_recognition)
[![Security](https://img.shields.io/badge/Security-Anti--Spoofing-purple.svg)]()

> Enterprise-grade biometric authentication system with liveness detection and real-time anti-spoofing.

---

## Overview

NOVA-SHIELD is a professional face recognition authentication system that distinguishes between real human faces and photos/videos. Built with computer vision and machine learning, it provides secure biometric authentication for applications like banking dashboards, access control systems, and identity verification.

---

## Features

| Category | Features |
|----------|----------|
| **Face Recognition** | High-accuracy face matching, Multiple face detection, Real-time processing |
| **Anti-Spoofing** | Blink detection, Head motion analysis, Texture frequency analysis, Reflection detection |
| **Liveness Detection** | Eye Aspect Ratio (EAR) calculation, Motion tracking, Screen/print attack prevention |
| **Banking Demo** | Account dashboard, Transaction history, Balance display |
| **Security** | Session management, Real-time verification, Spoof attempt logging |
| **UI/UX** | Glassmorphism design, Responsive layout, Professional interface |

---

## Technology Stack

- **Backend:** Flask (Python)
- **Face Recognition:** `face_recognition` + `dlib`
- **Computer Vision:** OpenCV
- **Anti-Spoofing:** FFT analysis, EAR calculation
- **Frontend:** HTML5, CSS3, JavaScript
- **Fonts:** Google Fonts (Inter)

---

# Installation

## Prerequisites

# System requirements
# - Python 3.8 or higher
# - Linux / macOS / Windows (WSL2 for camera)
# - Webcam (built-in or external)
# - 4GB RAM minimum

## Step 1: Clone Repository
git clone https://github.com/David-Kimath1/nova-shield.git
cd nova-shield

## Step 2: Create Virtual Environment
python3 -m venv venv
source venv/bin/activate
# On Windows:
# venv\script\activate

## Step 3: Install Dependencies
pip install --upgrade pip
pip install opencv-python face-recognition numpy flask scipy

## Step 4: Register Your Face
python3 register_first_face.py
Follow prompts:
Enter your name
Look at the camera
Press SPACE to capture
Press ESC to finish

## Step 5: Run the System
python3 liveness_shield.py
Open browser:
http://localhost:8080

## Usage
### Authenitcation Flow

### 1. Face Scanner Page
Camera activates automatically
Syste, detects face and analyzes liveness
Checks for blinks, motion and texture patterns
Green indicator = Live face detected
Orange indicator = Photo/Video detected

### 2. Verification Process
Real face: Shows confidence score and liveness percentage
Photo attact: Displays "PHOTO DETECTED" warning
Click "Verify Identity: or wait for auto-verification

### 3. Bank Dashboard
Shows account holder information
Display current balance
Lists recent transactions
Session remains active while face is present

## Anti Spoofing Tests

| Test Case                 | Expected Result                   |
| ------------------------- | --------------------------------- |
| Real face with blinks     | Access granted                    |
| Printed photo             | Access denied (Photo detected)    |
| Phone screen showing face | Access denied (Screen pattern)    |
| Video playback            | Access denied (No natural motion) |
| Real face with glasses    | Access granted (if registered)    |


## Face Registration
To register multiple users:
python3 register_first_face.py
Enter a different name for each user

## Configuration
Edit bank account details:
nano storage/bank_data.json
Example configuration:
{
    "name": "JOHN DOE",
    "account_number": "98-765-4321",
    "balance": 25000.00,
    "currency": "USD",
    "transactions": [
        {
            "date": "2024-01-15",
            "desc": "Deposit",
            "amount": "+1000",
            "type": "credit"
        },
        {
            "date": "2024-01-14",
            "desc": "Payment",
            "amount": "-50",
            "type": "debit"
        }
    ]
}

## Security Features
### Liveness Detection Methods
### Blink Detection (EAR)
Calculates Eye Aspect Ratio
Monitors natural blink patterns
Threshold: EAR < 0.2 indicates blink

### Head Motion Analysis
Tracks face position changes
Detects natural head movement
Rejects static images

### Texture Frequency Analysis
Applies FFT to face region
Detects screen moire patterns
Identifies print artifacts

### Reflection Detection
Identifies screen glare
Detects unnatural bright spots
Flags photo reflections

## Security Layers
Camera Input
     ↓
Face Detection
     ↓
Liveness Analysis ──→ Spoof Detection ──→ Reject
     ↓                    ↓
Face Recognition      Photo/Video Alert
     ↓
Authentication
     ↓
Session Grant

## Troubleshooting
### Camera Not Detected
ls /dev/video*
sudo chmod 666 /dev/video0

### Face Recognition Import Error
pip uninstall face_recognition dlib -y
pip install dlib
pip install face_recognition --no-cache-dir

### Bank Data Not Loading
python3 -c "import json; print(json.load(open('storage/bank_data.json')))"

### Recreate file:

mkdir -p storage
cat > storage/bank_data.json << 'EOF2'
{
    "name": "YOUR NAME",
    "account_number": "01-234-5678",
    "balance": 10000.00,
    "currency": "KES",
    "transactions": []
}
EOF2

### Port Already in Use
lsof -ti:8080 | xargs kill -9

## Performance
| Mode           | FPS   | Latency   |
| -------------- | ----- | --------- |
| CPU (HOG)      | 15-20 | 50-70ms   |
| Face Encoding  | 5-10  | 100-200ms |
| Liveness Check | 20-30 | 30-50ms   |

## Future Roadmap
Multi-factor authentication (face + voice)
Remote device locking
Mobile companion app
Cloud dashboard
Encrypted biometric storage
Federated learning for privacy
Edge AI processing
Multi-camera support

## Contributing
1. Fork the repository
2. Create feature branch
git checkout -b feature/AmazingFeature
3. Commit changes:
git commit -m 'Add AmazingFeature'
4. Push to branch:
git push origin feature/AmazingFeature
5. Open Pull Request

## License
Distributed under the MIT License. See LICENSE for more information.

## Author
### David Kimathi
Github @David-Kimath1

## Acknowledgments
face_recognition library by Adam Geitgey
dlib by Davis King
OpenCV community
Flask framework

<div align="center">

Built with Python and OpenCV | For Secure Authentication

Report Bug · Request Feature
</div>

