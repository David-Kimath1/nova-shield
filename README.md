# NOVA-SHIELD

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv" />
  <img src="https://img.shields.io/badge/Flask-Backend-black?style=for-the-badge&logo=flask" />
  <img src="https://img.shields.io/badge/AI-Face%20Recognition-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Security-Anti--Spoofing-green?style=for-the-badge" />
</p>

<p align="center">
  Enterprise-grade biometric authentication system with AI-powered liveness detection and anti-spoofing protection.
</p>

---

# ◆ Overview

NOVA-SHIELD is an AI-powered biometric authentication system designed to distinguish between real human faces and spoof attacks such as:

- Printed photos
- Mobile screen attacks
- Replay videos
- Static face images

The system combines facial recognition, computer vision, and liveness detection to provide secure authentication for:

- Banking systems
- Secure dashboards
- Identity verification
- Access control systems

---

# ◆ Features

| Module | Capabilities |
|--------|--------------|
| Face Recognition | Real-time face matching, Multiple face detection, High-accuracy recognition |
| Anti-Spoofing | Blink detection, Motion tracking, Reflection analysis, FFT texture detection |
| Liveness Detection | EAR calculation, Natural movement verification, Screen/photo rejection |
| Banking Dashboard | Account display, Transactions, Secure authentication |
| Security Layer | Session validation, Real-time verification, Spoof logging |
| Interface | Glassmorphism UI, Responsive design, Professional layout |

---

# ◆ Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Face Recognition | `face_recognition`, `dlib` |
| Computer Vision | OpenCV |
| Anti-Spoofing | FFT Analysis, EAR Detection |
| Frontend | HTML5, CSS3, JavaScript |
| Styling | Google Fonts (Inter) |

---

# ◆ Installation

## ◉ Prerequisites

System requirements:

- Python 3.8+
- Linux / macOS / Windows
- Webcam
- Minimum 4GB RAM

---

## ◉ Setup Process

### ■ Clone Repository

```bash
git clone https://github.com/David-Kimath1/nova-shield.git
cd nova-shield
```

---

### ■ Create Virtual Environment

#### ▶ Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### ▶ Windows

```bash
venv\Scripts\activate
```

---

### ■ Install Dependencies

```bash
pip install --upgrade pip
pip install opencv-python face-recognition numpy flask scipy
```

---

### ■ Register Your Face

```bash
python3 register_first_face.py
```

Follow prompts:

- Enter username
- Look at camera
- Press `SPACE` to capture
- Press `ESC` to finish

---

### ■ Run System

```bash
python3 liveness_shield.py
```

Open browser:

```bash
http://localhost:8080
```

---

# ◆ Authentication Flow

## ◉ Face Scanner

| Indicator | Meaning |
|-----------|----------|
| LIVE | Real human face detected |
| SPOOF | Photo/video attack detected |
| DENIED | Verification failed |

---

## ◉ Real Face Verification

### ■ Authentication Success

- Face matched successfully
- Liveness score calculated
- Secure session created
- Dashboard unlocked

---

## ◉ Spoof Detection

### ■ Blocked Attacks

The system automatically blocks:

- Printed photos
- Phone replay attacks
- Video playback attacks
- Static face images

Spoof attempts are logged in real time.

---

# ◆ Banking Dashboard

## ◉ Dashboard Features

The integrated banking demo includes:

- Account holder information
- Current balance display
- Transaction history
- Session verification
- Real-time identity validation

### ■ Session Protection

User sessions remain active only while the verified face is present.

---

# ◆ Security Architecture

```text
Camera Input
     │
     ▼
Face Detection
     │
     ▼
Liveness Analysis ───────► Spoof Detection ───────► Reject
     │                              │
     ▼                              ▼
Face Recognition              Photo/Video Alert
     │
     ▼
Authentication
     │
     ▼
Secure Session
```

---

# ◆ Liveness Detection Methods

## ◉ Blink Detection (EAR)

### ■ Eye Aspect Ratio Analysis

- Detects natural blinking patterns
- Rejects static image attacks
- Improves live verification accuracy

---

## ◉ Head Motion Analysis

### ■ Movement Tracking

- Tracks natural face movement
- Detects frozen/static attacks
- Enhances spoof detection reliability

---

## ◉ Texture Frequency Analysis

### ■ FFT Pattern Detection

- Detects monitor artifacts
- Identifies screen moire patterns
- Detects printed texture inconsistencies

---

## ◉ Reflection Detection

### ■ Reflection Analysis

- Detects glare from screens
- Identifies unnatural reflections
- Helps block replay attacks

---

# ◆ Anti-Spoofing Tests

| Test Case | Result |
|-----------|--------|
| Real face with blinking | GRANTED |
| Printed photo | REJECTED |
| Mobile screen replay | REJECTED |
| Video playback attack | REJECTED |
| Registered user with glasses | GRANTED |

---

# ◆ Configuration

## ◉ Register Multiple Users

### ■ Add Additional Faces

```bash
python3 register_first_face.py
```

Use a unique username for each user.

---

## ◉ Banking Data Configuration

### ■ Edit Banking Information

Modify:

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

# ◆ Troubleshooting

## ◉ Camera Not Detected

### ■ Linux Camera Permissions

```bash
ls /dev/video*
sudo chmod 666 /dev/video0
```

---

## ◉ face_recognition Import Error

### ■ Reinstall Dependencies

```bash
pip uninstall face_recognition dlib -y
pip install dlib
pip install face_recognition --no-cache-dir
```

---

## ◉ Invalid Banking JSON

### ■ Validate Configuration File

```bash
python3 -c "import json; print(json.load(open('storage/bank_data.json')))"
```

---

### ■ Recreate JSON File

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

## ◉ Port Already In Use

### ■ Kill Running Process

```bash
lsof -ti:8080 | xargs kill -9
```

---

# ◆ Performance

| Component | Performance |
|-----------|-------------|
| CPU Face Detection | 15–20 FPS |
| Face Encoding | 5–10 FPS |
| Liveness Detection | 20–30 FPS |
| Average Latency | 30–70ms |

---

# ◆ Future Roadmap

## ◉ Planned Features

- Voice + Face multi-factor authentication
- Remote device locking
- Mobile companion application
- Cloud dashboard integration
- Encrypted biometric storage
- Federated learning
- Edge AI optimization
- Multi-camera support

---

# ◆ Contributing

## ◉ Development Workflow

### ■ Create Feature Branch

```bash
git checkout -b feature/AmazingFeature
```

---

### ■ Commit Changes

```bash
git commit -m "Add AmazingFeature"
```

---

### ■ Push Changes

```bash
git push origin feature/AmazingFeature
```

---

### ■ Open Pull Request

Submit your pull request for review.

---

# ◆ License

Distributed under the MIT License.

See `LICENSE` for more information.

---

# ◆ Author

## ◉ Developer Information

| Platform | Link |
|----------|------|
| GitHub | https://github.com/David-Kimath1 |

---

# ◆ Acknowledgments

## ◉ Libraries & Frameworks

- `face_recognition` by Adam Geitgey
- `dlib` by Davis King
- OpenCV Community
- Flask Framework
