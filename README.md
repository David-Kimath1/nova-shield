NOVA-SHIELD
Category	Features
Core Security	Face recognition login, Multi-face detection, Continuous identity verification, Automatic system lock
Anti-Spoofing	Blink detection, Head movement tracking, Texture analysis, Photo/video attack prevention
AI Monitoring	Behavioral learning, Anomaly detection, Usage pattern analysis, Smart security scoring
Alerts	Telegram notifications, SMS alerts, Email alerts, Intruder snapshots
Hardware	GPU/CUDA acceleration, CPU fallback, Automatic backend selection
Encryption	AES-256 biometric vault, Secure key management, No plain image storage
Dashboard	Live camera feed, Real-time status, Intruder logs, Web-based control
Linux Integration	PAM module (optional), Systemd daemon, Startup applications

# Quick Start
# Clone repository
git clone https://github.com/David-Kimath1/nova-shield.git

# Enter project directory
cd nova-shield

# Make scripts executable
chmod +x scripts/*.sh

# Install dependencies
./scripts/install_deps.sh

# Register your face
python3 register_first_face.py

# Start the shield
python3 minimal_shield.py

| Requirement | Minimum                          |
| ----------- | -------------------------------- |
| OS          | Linux Mint / Ubuntu 20.04+       |
| Python      | Python 3.8+                      |
| RAM         | 4GB                              |
| Webcam      | Required                         |
| GPU         | Optional (NVIDIA CUDA supported) |

1. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate
2. Upgrade Pip
pip install --upgrade pip
3. Install Core Dependencies
pip install opencv-python face-recognition numpy
pip install flask flask-socketio aiohttp
pip install cryptography pyyaml python-dotenv
4. Optional GPU Setup
./scripts/setup_gpu.sh
5. Configure Environment Variables
cp .env.example .env
nano .env

Add your API keys and configurations inside .env.

6. Optional PAM Authentication Integration
cd pam
sudo ./install.sh
cd ..
Usage
Activate Environment
source venv/bin/activate
Register Face
python3 register_first_face.py
Start Security System
python3 minimal_shield.py
Start Web Dashboard
python3 gui/dashboard.py
Run as Background Service
sudo systemctl start nova-shield
Keyboard Shortcuts
Key	Action
q	Quit application
r	Register new face
SPACE	Capture face
ESC	Cancel operation
Commands Reference
View Intruder Logs
cat storage/logs/intrusions.json | jq '.[-5:]'
View Captured Intruders
ls -la storage/intruders/
Check Service Status
systemctl status nova-shield
View Real-Time Logs
journalctl -u nova-shield -f
Lock System Immediately
python3 -c "from security.lock_controller import LockController; LockController().lock()"
Project Structure
nova-shield/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── logger.py
│   └── event_bus.py
│
├── core/
│   ├── engine.py
│   ├── decision_engine.py
│   └── risk_model.py
│
├── vision/
│   ├── camera_stream.py
│   ├── frame_processor.py
│   ├── gpu_accelerator.py
│   └── cpu_fallback.py
│
├── recognition/
│   ├── face_encoder.py
│   ├── face_matcher.py
│   └── model_loader.py
│
├── antispoof/
│   ├── blink_detector.py
│   ├── motion_analyzer.py
│   └── texture_check.py
│
├── ai/
│   ├── behavior_model.py
│   └── anomaly_detector.py
│
├── security/
│   ├── action_handler.py
│   ├── lock_controller.py
│   └── intrusion_logger.py
│
├── notifications/
│   ├── telegram_alert.py
│   ├── sms_alert.py
│   └── alert_router.py
│
├── gui/
│   ├── dashboard.py
│   ├── templates/
│   └── static/
│
├── hardware/
│   ├── gpu_detector.py
│   └── backend_selector.py
│
├── encryption/
│   ├── vault.py
│   └── key_manager.py
│
├── pam/
│   ├── pam_nova.c
│   ├── build.sh
│   └── install.sh
│
├── storage/
│   ├── intruders/
│   ├── logs/
│   └── encrypted/
│
├── scripts/
│   ├── install_deps.sh
│   ├── setup_gpu.sh
│   └── run.sh
│
├── tests/
│   ├── test_face.py
│   ├── test_spoof.py
│   └── test_notifications.py
│
├── config.yaml
├── requirements.txt
└── README.md
Security
Encryption Standards
Data Type	Method	Key Length
Face Encodings	AES-256	256-bit
User Profiles	Fernet	128-bit
Behavioral Data	Encrypted JSON	256-bit
Security Layers
[Camera Input]
     ↓
[Face Detection] → [Anti-Spoofing] → [Liveness Check]
     ↓                    ↓                  ↓
[Face Matching] ← [Risk Scoring] ← [Behavior AI]
     ↓
[Decision Engine]
     ↓
[ALLOW] [ALERT] [LOCK]
Risk Scoring Weights
Feature	Weight
Face Match	35%
Liveness Detection	30%
Motion Analysis	20%
Behavior Score	15%
Troubleshooting
Camera Not Detected
ls /dev/video*
sudo chmod 666 /dev/video0
Face Recognition Import Error
pip uninstall face_recognition dlib -y
pip install dlib
pip install face_recognition --no-cache-dir

GPU Not Detected
nvidia-smi

If there is no output:

Email: david.kimathi@example.com
GitHub Issues: David-Kimath1/nova-shield/issues
<div align="center">

Built with Python and OpenCV for Linux Mint
</div>