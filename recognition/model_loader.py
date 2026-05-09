"""Loads GPU/CPU model dynamically"""

import importlib
from app.logger import get_logger


class ModelLoader:
    """Dynamically loads appropriate model based on hardware"""
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.logger = get_logger(__name__)
        self.model = None
        
    def load_face_model(self):
        """Load face recognition model"""
        if self.device == "cuda" or self.device == "mps":
            self.logger.info("[GPU] Loading GPU-accelerated face model")
            # Load GPU-optimized model
            from vision.gpu_accelerator import GPUAccelerator
            self.accelerator = GPUAccelerator()
        else:
            self.logger.info("[CPU] Loading CPU-optimized face model")
            from vision.cpu_fallback import CPUFallback
            self.fallback = CPUFallback()
            
        # Face recognition model is usually CPU-based
        import face_recognition
        return face_recognition
        
    def load_deep_learning_model(self, model_name: str):
        """Load deep learning model on appropriate device"""
        try:
            import torch
            
            if self.device == "cuda":
                return torch.load(model_name, map_location='cuda')
            else:
                return torch.load(model_name, map_location='cpu')
                
        except ImportError:
            self.logger.warning("[WARN] PyTorch not available, using fallback")
            return None