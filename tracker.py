"""
Модуль для отслеживания объектов между кадрами
"""
import math
from typing import Dict, List, Tuple
import config


class Tracker:
    """Класс для отслеживания объектов между кадрами"""
    
    def __init__(self, distance_threshold: int = None):
        """
        Инициализирует трекер
        
        Args:
            distance_threshold: Пороговое расстояние для сопоставления объектов
        """
        self.center_points: Dict[int, Tuple[int, int]] = {}
        self.id_count = 0
        self.distance_threshold = distance_threshold or config.TRACKER_DISTANCE_THRESHOLD
    
    def update(self, objects_rect: List[List[int]]) -> List[List[int]]:
        """
        Обновляет трекер с новыми обнаружениями
        
        Args:
            objects_rect: Список объектов в формате [x1, y1, x2, y2]
            
        Returns:
            List[List[int]]: Список объектов с ID в формате [x1, y1, x2, y2, id]
        """
        objects_bbs_ids = []
        
        for rect in objects_rect:
            x1, y1, x2, y2 = rect
            cx, cy = self._calculate_center(x1, y1, x2, y2)
            
            # Пытаемся найти существующий объект
            matched_id = self._find_matching_object(cx, cy)
            
            if matched_id is not None:
                # Обновляем существующий объект
                self.center_points[matched_id] = (cx, cy)
                objects_bbs_ids.append([x1, y1, x2, y2, matched_id])
            else:
                # Создаем новый объект
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x1, y1, x2, y2, self.id_count])
                self.id_count += 1
        
        # Удаляем объекты, которые больше не обнаружены
        active_ids = {obj[4] for obj in objects_bbs_ids}
        self.center_points = {obj_id: self.center_points[obj_id] 
                             for obj_id in active_ids if obj_id in self.center_points}
        
        return objects_bbs_ids
    
    def _calculate_center(self, x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
        """
        Вычисляет центр объекта
        
        Args:
            x1, y1: Левая верхняя точка
            x2, y2: Правая нижняя точка
            
        Returns:
            Tuple[int, int]: Координаты центра
        """
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return cx, cy
    
    def _find_matching_object(self, cx: int, cy: int) -> int | None:
        """
        Находит объект, ближайший к заданной точке
        
        Args:
            cx, cy: Координаты центра для поиска
            
        Returns:
            int | None: ID найденного объекта или None
        """
        for obj_id, (pt_x, pt_y) in self.center_points.items():
            distance = math.hypot(cx - pt_x, cy - pt_y)
            if distance < self.distance_threshold:
                return obj_id
        return None
    
    def reset(self):
        """Сбрасывает трекер"""
        self.center_points.clear()
        self.id_count = 0