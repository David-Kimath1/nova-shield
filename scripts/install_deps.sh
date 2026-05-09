#!/bin/bash
# Install all dependencies for NOVA-SHIELD

echo "========================================="
echo "NOVA-SHIELD Dependency Installer"
echo "========================================="

# Update system
echo "[1/6] Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
echo "[2/6] Installing Python packages..."
pip3 install -r requirements.txt

# Install system dependencies
echo "[3/6] Installing system packages..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    libopencv-dev \
    python3-opencv \
    cmake \
    build-essential \
    libpam0g-dev \
    libssl-dev \
    libffi-dev

# Install face recognition dependencies
echo "[4/6] Installing face_recognition..."
pip3 install face_recognition dlib

# Install PAM development files
echo "[5/6] Setting up PAM module..."
cd pam && ./build.sh && cd ..

# Create directories
echo "[6/6] Creating directories..."
mkdir -p storage/intruders
mkdir -p storage/logs
mkdir -p storage/encrypted
mkdir -p /tmp/nova-shield

# Set permissions
chmod 755 storage
chmod 700 storage/encrypted
chmod 700 .env 2>/dev/null

echo "========================================="
echo "[OK] Installation complete!"
echo "========================================="