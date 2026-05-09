"""Selects appropriate backend (GPU or CPU)"""

from hardware.gpu_detector import GPUDetector
from app.logger import get_logger


class BackendSelector:
    """Automatically selects best available backend"""
    
    def __init__(self):
        self.gpu_detector = GPUDetector()
        self.logger = get_logger(__name__)
        
    def select_backend(self) -> str:
        """
        Select best available backend
        Returns: 'cuda', 'mps' (macOS), or 'cpu'
        """
        # Check for CUDA GPU
        if self.gpu_detector.has_cuda():
            self.logger.info("[GPU] Selecting CUDA backend for acceleration")
            return 'cuda'
            
        # Check for MPS (Apple Silicon)
        try:
            import torch
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.logger.info("[GPU] Selecting MPS backend for Apple Silicon")
                return 'mps'
        except:
            pass
            
        # Fallback to CPU
        self.logger.info("[CPU] No GPU detected, using CPU backend")
        return 'cpu'
        
    def get_device_string(self) -> str:
        """Get device string for model loading"""
        backend = self.select_backend()
        
        if backend == 'cuda':
            return 'cuda:0'
        elif backend == 'mps':
            return 'mps'
        else:
            return 'cpu'