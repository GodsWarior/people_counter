"""
Модуль для загрузки и инициализации YOLO модели
"""
import numpy as np
from ultralytics import YOLO
from typing import Optional
import device_manager


def load_model(model_path: str, device: str) -> Optional[YOLO]:
    """
    Загружает YOLO модель и проверяет работу с устройством
    
    Args:
        model_path: Путь к файлу модели
        device: Устройство для вычислений ('cuda' или 'cpu')
        
    Returns:
        YOLO модель или None в случае ошибки
    """
    try:
        print("Loading YOLO model...")
        model = YOLO(model_path)
        print("✓ Model loaded successfully")
        
        # Проверяем, что CUDA действительно работает с YOLO
        if device == 'cuda':
            if test_cuda(model):
                print("✓ CUDA working - model will use GPU for inference")
            else:
                print("⚠ CUDA test failed - falling back to CPU")
                device = 'cpu'
        else:
            print("⚠ Using CPU for inference (slower)")
            
        return model
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return None


def test_cuda(model: YOLO) -> bool:
    """
    Тестирует работу модели с CUDA
    
    Args:
        model: Загруженная YOLO модель
        
    Returns:
        bool: True если CUDA работает, False иначе
    """
    try:
        test_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        yolo_device = device_manager.get_yolo_device('cuda')
        _ = model.predict(test_frame, verbose=False, device=yolo_device)
        return True
    except Exception as e:
        print(f"⚠ CUDA test failed: {e}")
        return False

