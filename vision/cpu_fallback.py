"""CPU fallback when GPU not available"""

import numpy as np
from app.logger import get_logger


class CPUFallback:
    """CPU-based processing fallback"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("[CPU] Running in CPU fallback mode")
        
    def process_face(self, face_image: np.ndarray) -> np.ndarray:
        """Process face on CPU"""
        # CPU-optimized face processing
        # Use smaller image for faster processing
        if face_image.shape[0] > 300:
            scale = 300 / face_image.shape[0]
            new_width = int(face_image.shape[1] * scale)
            face_image = cv2.resize(face_image, (new_width, 300))
            
        return face_image
        
    def batch_process(self, items: list, process_func) -> list:
        """Process items in batches on CPU"""
        results = []
        for item in items:
            results.append(process_func(item))
        return results