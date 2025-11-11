# counter.py - упрощенная логика с одной зоной
"""
Модуль для подсчета людей, пересекающих заданную зону
"""
import cv2
import numpy as np
from typing import Dict, List, Tuple, Set
import config


class PeopleCounter:
    """Класс для подсчета людей, пересекающих зону"""

    def __init__(self, counting_zone: List[Tuple[int, int]]):
        """
        Инициализирует счетчик людей

        Args:
            counting_zone: Координаты зоны подсчета (полигон)
        """
        self.counting_zone = np.array(counting_zone, np.int32)
        self.tracked_objects: Dict[int, bool] = {}  # {id: был_ли_в_зоне}
        self.total_count: Set[int] = set()  # Уникальные ID всех подсчитанных людей

    def update(self, objects_bbs_ids: List[List[int]]) -> int:
        """
        Обновляет счетчики на основе текущих позиций объектов

        Args:
            objects_bbs_ids: Список объектов в формате [x1, y1, x2, y2, id]

        Returns:
            int: общее количество прошедших людей
        """
        for bbox in objects_bbs_ids:
            x1, y1, x2, y2, obj_id = bbox

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2  # Центр объекта

            # Проверка пересечения с зоной
            in_zone = cv2.pointPolygonTest(self.counting_zone, (center_x, center_y), False) >= 0

            # Если объект в зоне и еще не был подсчитан
            if in_zone and obj_id not in self.total_count:
                self.total_count.add(obj_id)
                self.tracked_objects[obj_id] = True

        return len(self.total_count)

    def get_count(self) -> int:
        """
        Возвращает текущий счетчик

        Returns:
            int: общее количество прошедших людей
        """
        return len(self.total_count)

    def is_in_zone(self, obj_id: int) -> bool:
        """Проверяет, находится ли объект в зоне"""
        return self.tracked_objects.get(obj_id, False)