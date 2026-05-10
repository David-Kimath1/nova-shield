# NOVA-SHIELD

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://linux.org)
[![Face Recognition](https://img.shields.io/badge/Face%20Recognition-AI-red.svg)](https://github.com/ageitgey/face_recognition)
[![Security](https://img.shields.io/badge/Security-Anti--Spoofing-purple.svg)]()

> Enterprise-grade biometric authentication system with liveness detection and real-time anti-spoofing.

---

## Overview

NOVA-SHIELD is a professional face recognition authentication system designed to distinguish between real human faces and spoof attacks such as photos, videos, and screen replays.

Built with computer vision and machine learning, the system provides secure biometric authentication for applications such as:

- Banking dashboards
- Access control systems
- Identity verification
- Secure login systems

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

## Installation

### Prerequisites

System requirements:

- Python 3.8 or higher
- Linux / macOS / Windows
- Webcam (built-in or external)
- 4GB RAM minimum

---

### Step 1: Clone Repository

```bash
git clone https://github.com/David-Kimath1/nova-shield.git
cd nova-shield
```

---

### Step 2: Create Virtual Environment

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

---

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install opencv-python face-recognition numpy flask scipy
```

---

### Step 4: Register Your Face

```bash
python3 register_first_face.py
```

Follow the prompts:

- Enter your name
- Look at the camera
- Press `SPACE` to capture
- Press `ESC` to finish

---

### Step 5: Run the System

```bash
python3 liveness_shield.py
```

Open your browser:

```bash
http://localhost:8080
```

---

# Usage

## Authentication Flow

### Face Scanner Page

- Camera activates automatically
- System detects faces in real time
- Liveness analysis starts instantly
- Blink and motion tracking are monitored
- Texture analysis checks for screen/photo attacks

### Detection Results

| Result | Meaning |
|--------|---------|
| 🟢 Green Indicator | Live human face detected |
| 🟠 Orange Indicator | Photo/video spoof detected |
| 🔴 Access Denied | Verification failed |

---

## Verification Process

### Real Face

- Confidence score displayed
- Liveness percentage shown
- User authentication granted
- Dashboard access enabled

### Photo / Video Attack

- "PHOTO DETECTED" warning displayed
- Access denied automatically
- Spoof attempt logged

---

# Banking Dashboard

The included banking demo interface provides:

- Account holder information
- Current balance display
- Recent transaction history
- Secure session handling

The session remains active only while the verified face is present.

---

# Anti-Spoofing Tests

| Test Case | Expected Result |
|-----------|----------------|
| Real face with blinks | ✅ Access granted |
| Printed photo | ❌ Access denied |
| Phone screen showing face | ❌ Access denied |
| Video playback attack | ❌ Access denied |
| Real face with glasses | ✅ Access granted |

---

# Configuration

## Register Multiple Users

Run:

```bash
python3 register_first_face.py
```

Enter a different name for each user.

---

## Modify Banking Data

Edit:

```bash
storage/bank_data.json
```

Example configuration:

```json
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
```

---

# Security Features

## Liveness Detection Methods

### Blink Detection (EAR)

- Calculates Eye Aspect Ratio
- Detects natural blinking patterns
- Helps reject static photo attacks

### Head Motion Analysis

- Tracks face movement
- Detects natural motion behavior
- Prevents spoofing using fixed images

### Texture Frequency Analysis

- Uses FFT analysis
- Detects screen moire patterns
- Identifies printed image artifacts

### Reflection Detection

- Detects screen glare
- Flags unnatural reflections
- Helps identify phone or monitor attacks

---

# Security Layers

```text
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
```

---

# Troubleshooting

## Camera Not Detected

```bash
ls /dev/video*
sudo chmod 666 /dev/video0
```

---

## face_recognition Import Error

```bash
pip uninstall face_recognition dlib -y
pip install dlib
pip install face_recognition --no-cache-dir
```

---

## Bank Data Not Loading

Check JSON validity:

```bash
python3 -c "import json; print(json.load(open('storage/bank_data.json')))"
```

Recreate the file if corrupted:

```bash
mkdir -p storage
```

```bash
cat > storage/bank_data.json << 'EOF'
{
    "name": "YOUR NAME",
    "account_number": "01-234-5678",
    "balance": 10000.00,
    "currency": "KES",
    "transactions": []
}
EOF
```

---

## Port Already in Use

```bash
lsof -ti:8080 | xargs kill -9
```

---

# Performance

| Mode | FPS | Latency |
|------|-----|----------|
| CPU (HOG) | 15–20 FPS | 50–70ms |
| Face Encoding | 5–10 FPS | 100–200ms |
| Liveness Check | 20–30 FPS | 30–50ms |

---

# Future Roadmap

- Multi-factor authentication (Face + Voice)
- Remote device locking
- Mobile companion application
- Cloud dashboard
- Encrypted biometric storage
- Federated learning for privacy
- Edge AI processing
- Multi-camera support

---

# Contributing

1. Fork the repository
2. Create your feature branch

```bash
git checkout -b feature/AmazingFeature
```

3. Commit your changes

```bash
git commit -m "Add AmazingFeature"
```

4. Push to the branch

```bash
git push origin feature/AmazingFeature
```

5. Open a Pull Request

---

# License

Distributed under the MIT License.

See the `LICENSE` file for more information.

---

# Author

## David Kimathi

- GitHub: https://github.com/David-Kimath1

---

# Acknowledgments

- `face_recognition` library by Adam Geitgey
- `dlib` by Davis King
- OpenCV community
- Flask framework
