# 🛡️ NOVA-SHIELD

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![OS](https://img.shields.io/badge/OS-Linux%20Mint%20%2F%20Ubuntu-green.svg)](https://linuxmint.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/David-Kimath1/nova-shield)](https://github.com/David-Kimath1/nova-shield/issues)

**NOVA-SHIELD** is an advanced biometric security layer designed for Linux environments. It combines real-time face recognition, anti-spoofing countermeasures, and AI-driven behavioral monitoring to ensure your system remains secure even when you step away.

---

## 🚀 Features

| Category | Key Features |
| :--- | :--- |
| **Core Security** | Face recognition login, Multi-face detection, Continuous identity verification, Auto-lock |
| **Anti-Spoofing** | Blink detection, Head movement tracking, Texture analysis, Photo/video attack prevention |
| **AI Monitoring** | Behavioral learning, Anomaly detection, Usage pattern analysis, Smart security scoring |
| **Alerts** | Telegram notifications, SMS alerts, Email alerts, Intruder snapshots |
| **Hardware** | GPU/CUDA acceleration, CPU fallback, Automatic backend selection |
| **Encryption** | AES-256 biometric vault, Secure key management, No plain image storage |
| **Dashboard** | Live camera feed, Real-time status, Intruder logs, Web-based control |

---

## 🛠️ Quick Start

### 1. Installation
```bash
# Clone repository
git clone [https://github.com/David-Kimath1/nova-shield.git](https://github.com/David-Kimath1/nova-shield.git)
cd nova-shield

# Make scripts executable
chmod +x scripts/*.sh

# Install system dependencies
./scripts/install_deps.sh

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Register your face (Primary User)
python3 register_first_face.py

# Start the core security shield
python3 minimal_shield.py

Requirement,Minimum Specification
OS,Linux Mint / Ubuntu 20.04+
Python,3.8+
RAM,4GB
Webcam,Standard USB or Integrated
GPU,Optional (NVIDIA CUDA supported for faster inference)

## 🛡️ Security Architecture

**NOVA-SHIELD** operates on a multi-layered verification pipeline to ensure zero-trust security.

1. **Ingestion**: Real-time frame capture via `vision/camera_stream.py`.
2. **Verification**: Parallel processing of Face Matching, Liveness Detection, and Behavioral Scoring.
3. **Action**: The Decision Engine evaluates the weighted risk score to trigger `ALLOW`, `ALERT`, or `LOCK` commands.

### Risk Scoring Weights
* **Face Match**: 35%
* **Liveness Detection**: 30%
* **Motion Analysis**: 20%
* **Behavior Score**: 15%

---

## 📂 Project Structure

```text
nova-shield/
├── core/            # Decision engine & risk modeling
├── vision/          # Camera stream & frame processing
├── recognition/     # Face encoding & matching
├── antispoof/       # Blink & texture analysis
├── ai/              # Behavioral anomaly detection
├── security/        # System lock & action handlers
├── notifications/   # Telegram, SMS, & Email logic
├── gui/             # Web-based dashboard & templates
├── pam/             # Optional Linux PAM integration
└── storage/         # Encrypted logs & intruder snapshots

Shortcuts & Commands

Keyboard Shortcuts
Key,Action
q,Quit application
r,Register new face
SPACE,Capture face
ESC,Cancel operation

CLI Reference

    View Intruder Logs: cat storage/logs/intrusions.json | jq '.[-5:]'

    Check Service Status: systemctl status nova-shield

    Force Lock System: python3 -c "from security.lock_controller import LockController; LockController().lock()"

🔧 Troubleshooting
Camera Not Detected
Bash

ls /dev/video*
sudo chmod 666 /dev/video0

Face Recognition Import Error

If dlib fails to compile, ensure you have build-essentials installed:
Bash

pip uninstall face_recognition dlib -y
pip install dlib
pip install face_recognition --no-cache-dir

📬 Contact & Support

    Developer: David Kimathi

    Email: david.kimathi@example.com

    GitHub Issues: David-Kimath1/nova-shield/issues