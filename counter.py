"""
Модуль для подсчета людей, пересекающих заданные области
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Set
import config


class PeopleCounter:
    """Класс для подсчета людей, пересекающих зоны"""
    
    def __init__(self, area1: List[Tuple[int, int]], area2: List[Tuple[int, int]]):
        """
        Инициализирует счетчик людей
        
        Args:
            area1: Координаты первой области (полигон)
            area2: Координаты второй области (полигон)
        """
        self.area1 = np.array(area1, np.int32)
        self.area2 = np.array(area2, np.int32)
        self.going_out: Dict[int, Tuple[int, int]] = {}
        self.going_in: Dict[int, Tuple[int, int]] = {}
        self.counter1: Set[int] = set()  # Выходящие
        self.counter2: Set[int] = set()  # Входящие
    
    def update(self, objects_bbs_ids: List[List[int]]) -> Tuple[int, int]:
        """
        Обновляет счетчики на основе текущих позиций объектов
        
        Args:
            objects_bbs_ids: Список объектов в формате [x1, y1, x2, y2, id]
            
        Returns:
            Tuple[int, int]: (количество вышедших, количество вошедших)
        """
        for bbox in objects_bbs_ids:
            x1, y1, x2, y2, obj_id = bbox
            
            center_x = (x1 + x2) // 2
            center_y = y2  # Нижняя точка
            
            # Проверка пересечения с областями
            self._check_area2(center_x, center_y, obj_id)
            self._check_area1(center_x, center_y, obj_id)
        
        return len(self.counter1), len(self.counter2)
    
    def _check_area2(self, center_x: int, center_y: int, obj_id: int):
        """Проверяет пересечение с областью 2 (выход)"""
        if cv2.pointPolygonTest(self.area2, (center_x, center_y), False) >= 0:
            self.going_out[obj_id] = (center_x, center_y)
    
    def _check_area1(self, center_x: int, center_y: int, obj_id: int):
        """Проверяет пересечение с областью 1 (вход)"""
        # Если объект был в области 2 и теперь в области 1 - он вышел
        if obj_id in self.going_out:
            if cv2.pointPolygonTest(self.area1, (center_x, center_y), False) >= 0:
                self.counter1.add(obj_id)
        
        # Если объект в области 1 - отмечаем как входящий
        if cv2.pointPolygonTest(self.area1, (center_x, center_y), False) >= 0:
            self.going_in[obj_id] = (center_x, center_y)
        
        # Если объект был в области 1 и теперь в области 2 - он вошел
        if obj_id in self.going_in:
            if cv2.pointPolygonTest(self.area2, (center_x, center_y), False) >= 0:
                self.counter2.add(obj_id)
    
    def get_counters(self) -> Tuple[int, int]:
        """
        Возвращает текущие счетчики
        
        Returns:
            Tuple[int, int]: (количество вышедших, количество вошедших)
        """
        return len(self.counter1), len(self.counter2)
    
    def is_tracked_out(self, obj_id: int) -> bool:
        """Проверяет, отслеживается ли объект как выходящий"""
        return obj_id in self.going_out
    
    def is_tracked_in(self, obj_id: int) -> bool:
        """Проверяет, отслеживается ли объект как входящий"""
        return obj_id in self.going_in

