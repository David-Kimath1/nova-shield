# NOVA-SHIELD

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

*   **Backend:** Flask (Python)
*   **Face Recognition:** `face_recognition` + `dlib`
*   **Computer Vision:** OpenCV
*   **Anti-Spoofing:** FFT analysis, EAR calculation
*   **Frontend:** HTML5, CSS3, JavaScript
*   **Fonts:** Google Fonts (Inter)

---

## Installation

### Prerequisites

System requirements:
*   Python 3.8 or higher
*   Linux / macOS / Windows (WSL2 for camera)
*   Webcam (built-in or external)
*   4GB RAM minimum

### Step 1: Clone Repository
git clone [https://github.com/David-Kimath1/nova-shield.git](https://github.com/David-Kimath1/nova-shield.git)
cd nova-shield

Step 2: Create Virtual Environment
python3 -m venv venv
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

Step 3: Install Dependencies
pip install --upgrade pip
pip install opencv-python face-recognition numpy flask scipy

Step 4: Register Your Face
python3 register_first_face.py

Follow prompts:

    Enter your name

    Look at the camera

    Press SPACE to capture

    Press ESC to finish

    Step 5: Run the System
    python3 liveness_shield.py
    Open browser: http://localhost:8080

    UsageAuthentication FlowFace Scanner PageCamera activates automatically.System detects face and analyzes liveness.Checks for blinks, motion, and texture patterns.Green indicator = Live face detected.Orange indicator = Photo/Video detected.Verification ProcessReal face: Shows confidence score and liveness percentage.Photo attack: Displays "PHOTO DETECTED" warning.Click "Verify Identity" or wait for auto-verification.Bank DashboardShows account holder information.Displays current balance and recent transactions.Session remains active while face is present.Anti-Spoofing TestsTest CaseExpected ResultReal face with blinksAccess grantedPrinted photoAccess denied (Photo detected)Phone screen showing faceAccess denied (Screen pattern)Video playbackAccess denied (No natural motion)Real face with glassesAccess granted (if registered)ConfigurationFace RegistrationTo register multiple users, run:Bashpython3 register_first_face.py
Enter a different name for each user.Edit Bank DetailsModify the following file: storage/bank_data.jsonExample configuration:JSON{
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
Security FeaturesLiveness Detection MethodsBlink Detection (EAR): Calculates Eye Aspect Ratio and monitors natural blink patterns. Threshold: EAR < 0.2 indicates a blink.Head Motion Analysis: Tracks face position changes and detects natural head movement to reject static images.Texture Frequency Analysis: Applies FFT to the face region to detect screen moire patterns and identify print artifacts.Reflection Detection: Identifies screen glare and unnatural bright spots to flag photo reflections.Security LayersPlaintextCamera Input
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
TroubleshootingCamera Not DetectedBashls /dev/video*
sudo chmod 666 /dev/video0
Face Recognition Import ErrorBashpip uninstall face_recognition dlib -y
pip install dlib
pip install face_recognition --no-cache-dir
Bank Data Not LoadingCheck JSON validity:Bashpython3 -c "import json; print(json.load(open('storage/bank_data.json')))"
Recreate file if corrupted:Bashmkdir -p storage
cat > storage/bank_data.json << 'EOF2'
{
    "name": "YOUR NAME",
    "account_number": "01-234-5678",
    "balance": 10000.00,
    "currency": "KES",
    "transactions": []
}
EOF2
Port Already in UseBashlsof -ti:8080 | xargs kill -9
PerformanceModeFPSLatencyCPU (HOG)15-2050-70msFace Encoding5-10100-200msLiveness Check20-3030-50msFuture RoadmapMulti-factor authentication (face + voice)Remote device locking and mobile companion appCloud dashboard and encrypted biometric storageFederated learning for privacyEdge AI processing and multi-camera supportContributingFork the repository.Create your feature branch: git checkout -b feature/AmazingFeature.Commit your changes: git commit -m 'Add AmazingFeature'.Push to the branch: git push origin feature/AmazingFeature.Open a Pull Request.LicenseDistributed under the MIT License. See LICENSE for more information.AuthorDavid KimathiGitHub: @David-Kimath1Acknowledgmentsface_recognition library by Adam Geitgeydlib by Davis KingOpenCV communityFlask framework

