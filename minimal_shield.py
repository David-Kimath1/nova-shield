#!/usr/bin/env python3
"""
NOVA-SHIELD - Minimal Working Version
Runs as an application, NOT replacing login
"""

import cv2
import face_recognition
import numpy as np
from datetime import datetime
import os
import pickle
from pathlib import Path

class MinimalNovaShield:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.process_current_frame = True
        self.intruder_count = 0
        
        # Create storage
        Path("storage/intruders").mkdir(parents=True, exist_ok=True)
        
        # Load your face if registered
        self.load_known_faces()
        
    def load_known_faces(self):
        """Load registered faces"""
        known_file = Path("storage/known_faces.pkl")
        if known_file.exists():
            with open(known_file, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                print(f"[LOAD] Loaded {len(self.known_face_names)} registered faces")
        else:
            print("[INFO] No registered faces found. Run register_face.py first")
            
    def register_face(self, name):
        """Register a new face"""
        print(f"[REGISTER] Looking at camera to register {name}...")
        print("Press SPACE to capture, ESC to cancel")
        
        cap = cv2.VideoCapture(0)
        registered = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Show frame
            cv2.putText(frame, f"Registering: {name}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press SPACE to capture", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Face Registration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                # Capture and encode face
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if face_locations:
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    if face_encodings:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(name)
                        
                        # Save to disk
                        with open("storage/known_faces.pkl", 'wb') as f:
                            pickle.dump({
                                'encodings': self.known_face_encodings,
                                'names': self.known_face_names
                            }, f)
                        
                        print(f"[OK] Face registered for {name}")
                        registered = True
                        break
                    else:
                        print("[FAIL] Could not encode face, try again")
                else:
                    print("[FAIL] No face detected, try again")
                    
            elif key == 27:  # ESC
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return registered
        
    def run(self):
        """Main security loop"""
        print("[SHIELD] NOVA-SHIELD Active")
        print("[INFO] Press 'q' to quit")
        print("[INFO] Press 'r' to register new face")
        print("-" * 50)
        
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process every other frame for performance
            if self.process_current_frame:
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Find faces
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                
                # Scale back face locations
                self.face_locations = [(top*2, right*2, bottom*2, left*2) 
                                       for (top, right, bottom, left) in self.face_locations]
                
                self.face_names = []
                for face_encoding in self.face_encodings:
                    if self.known_face_encodings:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        
                        if True in matches:
                            best_match_index = np.argmin(distances)
                            name = self.known_face_names[best_match_index]
                            confidence = 1 - distances[best_match_index]
                            
                            if confidence > 0.6:
                                self.face_names.append(f"{name} ({confidence:.2f})")
                            else:
                                self.face_names.append("UNKNOWN")
                        else:
                            self.face_names.append("UNKNOWN")
                    else:
                        self.face_names.append("UNKNOWN")
                        
            self.process_current_frame = not self.process_current_frame
            
            # Draw results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                color = (0, 255, 0) if "UNKNOWN" not in name else (0, 0, 255)
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                # Save intruder snapshot
                if "UNKNOWN" in name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = f"storage/intruders/intruder_{timestamp}.jpg"
                    cv2.imwrite(path, frame)
                    print(f"[INTRUDER] Captured at {timestamp}")
                    self.intruder_count += 1
            
            # Show status
            cv2.putText(frame, f"KNOWN: {len(self.known_face_names)} | INTRUDERS: {self.intruder_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('NOVA-SHIELD', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                name = input("Enter name to register: ")
                self.register_face(name)
                
        cap.release()
        cv2.destroyAllWindows()
        print(f"[SHIELD] Shutdown. Total intruders detected: {self.intruder_count}")

if __name__ == "__main__":
    shield = MinimalNovaShield()
    shield.run()
