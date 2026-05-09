"""GPU acceleration for vision processing"""

import torch
import numpy as np
from typing import Optional


class GPUAccelerator:
    """Handles GPU-accelerated operations"""
    
    def __init__(self):
        self.device = self._get_device()
        self.available = self.device.type == 'cuda'
        
    def _get_device(self):
        """Get available compute device"""
        if torch.cuda.is_available():
            return torch.device('cuda')
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return torch.device('mps')
        else:
            return torch.device('cpu')
            
    def to_tensor(self, image: np.ndarray) -> torch.Tensor:
        """Convert numpy image to GPU tensor"""
        tensor = torch.from_numpy(image).float()
        if self.available:
            tensor = tensor.to(self.device)
        return tensor
        
    def to_numpy(self, tensor: torch.Tensor) -> np.ndarray:
        """Convert GPU tensor back to numpy"""
        if self.available:
            tensor = tensor.cpu()
        return tensor.numpy()
        
    def batch_process(self, images: list, model) -> list:
        """Process multiple images in batch on GPU"""
        if not images:
            return []
            
        # Stack images into batch
        batch = torch.stack([self.to_tensor(img) for img in images])
        
        with torch.no_grad():
            results = model(batch)
            
        return [self.to_numpy(r) for r in results]