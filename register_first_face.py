#!/usr/bin/env python3
"""Register your face first before running the shield"""

import cv2
import face_recognition
import pickle
from pathlib import Path

print("[SETUP] NOVA-SHIELD Face Registration")
print("=" * 50)
print("Look at the camera. Make sure your face is well-lit.")
print("Press SPACE to capture your face")
print("Press ESC to cancel")
print()

name = input("Enter your name: ")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.putText(frame, f"Look at camera to register: {name}", (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "Press SPACE to capture", (50, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow('Register Face', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 32:  # SPACE
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            if face_encodings:
                # Save to disk
                known_file = Path("storage/known_faces.pkl")
                known_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(known_file, 'wb') as f:
                    pickle.dump({
                        'encodings': [face_encodings[0]],
                        'names': [name]
                    }, f)
                
                print(f"\n[OK] Face registered for {name}!")
                print("[INFO] You can now run: python3 minimal_shield.py")
                break
            else:
                print("[FAIL] Could not encode face, try again")
        else:
            print("[FAIL] No face detected, try again")
            
    elif key == 27:  # ESC
        print("[CANCEL] Registration cancelled")
        break

cap.release()
cv2.destroyAllWindows()
