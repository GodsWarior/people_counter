"""
Модуль для расчета FPS (кадров в секунду)
"""
import time
from collections import deque
from typing import Deque


class FPSCalculator:
    """Класс для расчета FPS"""
    
    def __init__(self, window_size: int = 30):
        """
        Инициализирует калькулятор FPS
        
        Args:
            window_size: Размер окна для усреднения FPS
        """
        self.window_size = window_size
        self.fps_deque: Deque[float] = deque(maxlen=window_size)
        self.prev_time = 0
    
    def update(self) -> float:
        """
        Обновляет FPS на основе текущего времени
        
        Returns:
            float: Средний FPS за последние N кадров
        """
        curr_time = time.time()
        
        if self.prev_time > 0:
            fps = 1 / (curr_time - self.prev_time)
            self.fps_deque.append(fps)
        else:
            fps = 0
        
        self.prev_time = curr_time
        
        if len(self.fps_deque) > 0:
            avg_fps = sum(self.fps_deque) / len(self.fps_deque)
        else:
            avg_fps = 0
        
        return avg_fps
    
    def reset(self):
        """Сбрасывает калькулятор FPS"""
        self.fps_deque.clear()
        self.prev_time = 0

