# NOVA-SHIELD
## AI-Powered Biometric Security System for Linux

[NOVA] [SHIELD] - Your Face is the Key

### Features

- [FACE] Face recognition login
- [SHIELD] Anti-spoofing detection (blinks, motion, texture)
- [EYE] Continuous identity verification
- [BELL] Real-time intruder detection
- [BRAIN] AI behavior monitoring
- [BELL] Telegram & SMS alerts (Kenya-ready)
- [GPU] GPU/CPU smart acceleration
- [LOCK] Encrypted biometric vault
- [TERMINAL] Linux PAM integration
- [DASH] Live web dashboard
- [CLOCK] System daemon with auto-start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/nova-shield.git
cd nova-shield

# Run installation
chmod +x scripts/*.sh
sudo ./scripts/install_deps.sh

# Setup GPU (optional)
./scripts/setup_gpu.sh

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start system
sudo ./scripts/run.sh