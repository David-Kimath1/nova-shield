"""Frame preprocessing and face detection"""

import cv2
import face_recognition
from typing import List, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class FaceData:
    """Extracted face data"""
    bounding_box: tuple
    encoding: np.ndarray
    landmarks: dict
    image: np.ndarray


class ProcessedFrame:
    """Container for processed frame data"""
    
    def __init__(self, original_frame, faces: List[FaceData]):
        self.original_frame = original_frame
        self.faces = faces
        self.has_faces = len(faces) > 0


class FrameProcessor:
    """Processes camera frames for face detection"""
    
    def __init__(self, config, device: str = "cpu"):
        self.config = config
        self.device = device
        
    def process(self, frame: np.ndarray) -> ProcessedFrame:
        """
        Process frame to detect and extract faces
        """
        if frame is None:
            return ProcessedFrame(None, [])
            
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            return ProcessedFrame(frame, [])
            
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Get face landmarks
        face_landmarks = face_recognition.face_landmarks(rgb_frame, face_locations)
        
        faces = []
        for i, (location, encoding, landmarks) in enumerate(
            zip(face_locations, face_encodings, face_landmarks)
        ):
            # Extract face image
            top, right, bottom, left = location
            face_img = frame[top:bottom, left:right]
            
            faces.append(FaceData(
                bounding_box=location,
                encoding=encoding,
                landmarks=landmarks,
                image=face_img
            ))
            
        return ProcessedFrame(frame, faces)