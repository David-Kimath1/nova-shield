#!/bin/bash
# Setup CUDA for GPU acceleration

echo "========================================="
echo "NOVA-SHIELD GPU Setup"
echo "========================================="

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "[WARN] NVIDIA GPU not detected or drivers not installed"
    echo "Running in CPU mode..."
    exit 0
fi

echo "[GPU] NVIDIA GPU detected:"
nvidia-smi --query-gpu=name --format=csv,noheader

# Check CUDA version
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -d',' -f1)
    echo "[CUDA] Version: $CUDA_VERSION"
fi

# Install PyTorch with CUDA support
echo "[1/2] Installing PyTorch with CUDA..."
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install CUDA-enabled OpenCV
echo "[2/2] Installing OpenCV with CUDA..."
pip3 install opencv-python-headless opencv-contrib-python

# Verify installation
python3 -c "import torch; print(f'[OK] CUDA Available: {torch.cuda.is_available()}')"

echo "========================================="
echo "[OK] GPU setup complete!"
echo "========================================="