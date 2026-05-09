#!/usr/bin/env python3
"""Test NOVA-SHIELD system"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Config
from hardware.backend_selector import BackendSelector

print("[TEST] NOVA-SHIELD System Test")
print("-" * 40)

# Test config
config = Config()
print("[OK] Configuration loaded")

# Test backend selection
backend = BackendSelector()
device = backend.select_backend()
print(f"[OK] Backend selected: {device}")

# Check camera
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("[OK] Camera detected")
    cap.release()
else:
    print("[FAIL] No camera detected")

print("-" * 40)
print("[INFO] System ready for testing")
