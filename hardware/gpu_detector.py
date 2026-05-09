"""Detects GPU/CUDA availability"""

import subprocess
import sys
from app.logger import get_logger


class GPUDetector:
    """Detects available GPU hardware"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def has_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                self.logger.info(f"[GPU] CUDA available. Device: {torch.cuda.get_device_name(0)}")
            return cuda_available
        except ImportError:
            self.logger.debug("[GPU] PyTorch not installed")
            return False
            
    def has_nvidia_gpu(self) -> bool:
        """Check for NVIDIA GPU via nvidia-smi"""
        try:
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
            
    def get_gpu_info(self) -> dict:
        """Get detailed GPU information"""
        info = {
            'cuda_available': self.has_cuda(),
            'nvidia_gpu': self.has_nvidia_gpu(),
            'device_name': None,
            'memory_mb': 0
        }
        
        if info['cuda_available']:
            try:
                import torch
                info['device_name'] = torch.cuda.get_device_name(0)
                info['memory_mb'] = torch.cuda.get_device_properties(0).total_memory // (1024**2)
            except:
                pass
                
        return info