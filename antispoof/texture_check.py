"""Texture analysis to detect screen/photo spoofing"""

import cv2
import numpy as np
from skimage.feature import local_binary_pattern


class TextureChecker:
    """Detects fake faces using texture analysis"""
    
    def __init__(self):
        # LBP parameters
        self.radius = 1
        self.n_points = 8 * self.radius
        
    def detect_spoof(self, face_image: np.ndarray) -> dict:
        """
        Analyze face texture for spoofing indicators
        Returns dict with score and verdict
        """
        # Convert to grayscale
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        
        # Calculate LBP texture
        lbp = local_binary_pattern(gray, self.n_points, self.radius, method='uniform')
        
        # Calculate texture histogram
        hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, self.n_points + 3), range=(0, self.n_points + 2))
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-6)
        
        # Check for spoofing indicators
        # Real faces have more texture variation
        texture_variance = np.var(hist)
        
        # Check for screen moire patterns
        moire_score = self._detect_moire_patterns(gray)
        
        # Check for reflection artifacts (screen glare)
        reflection_score = self._detect_reflections(gray)
        
        spoof_score = (moire_score + reflection_score) / 2
        is_spoof = spoof_score > 0.6
        
        return {
            'is_spoof': is_spoof,
            'confidence': spoof_score,
            'texture_variance': texture_variance
        }
        
    def _detect_moire_patterns(self, image: np.ndarray) -> float:
        """Detect moire patterns typical of screen captures"""
        # Apply FFT to detect periodic patterns
        f = np.fft.fft2(image)
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        
        # Check for high-frequency peaks (moire patterns)
        high_freq = magnitude[int(image.shape[0]*0.4):int(image.shape[0]*0.6),
                              int(image.shape[1]*0.4):int(image.shape[1]*0.6)]
        
        if high_freq.size > 0:
            peak_ratio = np.max(high_freq) / (np.mean(high_freq) + 1e-6)
            return min(peak_ratio / 10, 1.0)
        return 0.0
        
    def _detect_reflections(self, image: np.ndarray) -> float:
        """Detect reflection artifacts from screens"""
        # Check for bright spots (glare)
        _, thresh = cv2.threshold(image, 240, 255, cv2.THRESH_BINARY)
        glare_ratio = np.sum(thresh > 0) / thresh.size
        
        return min(glare_ratio * 5, 1.0)  # Scale up small glare areas