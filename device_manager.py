"""
Модуль для управления устройством (CUDA/CPU)
"""
import torch
from typing import Tuple


def get_device() -> Tuple[str, dict]:
    """
    Определяет доступное устройство для вычислений
    
    Returns:
        Tuple[str, dict]: (device_name, device_info)
    """
    if torch.cuda.is_available():
        device = 'cuda'
        device_info = {
            'name': torch.cuda.get_device_name(0),
            'cuda_version': torch.version.cuda,
            'pytorch_version': torch.__version__,
            'device_count': torch.cuda.device_count()
        }
        print(f"✓ CUDA is available")
        print(f"✓ GPU: {device_info['name']}")
        print(f"✓ CUDA Version: {device_info['cuda_version']}")
        print(f"✓ PyTorch Version: {device_info['pytorch_version']}")
    else:
        device = 'cpu'
        device_info = {
            'pytorch_version': torch.__version__
        }
        print("⚠ CUDA is not available - using CPU")
        print("  Make sure you have:")
        print("  1. NVIDIA GPU with CUDA support")
        print("  2. CUDA toolkit installed")
        print("  3. PyTorch with CUDA support (install with: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118)")
    
    print(f"\nUsing device: {device.upper()}\n")
    return device, device_info


def get_yolo_device(device: str) -> int | str:
    """
    Преобразует device для использования в YOLO
    
    Args:
        device: 'cuda' или 'cpu'
        
    Returns:
        int | str: 0 для CUDA, 'cpu' для CPU
    """
    return 0 if device == 'cuda' else 'cpu'

