"""
Модуль для визуализации результатов на кадре
"""
import cv2
import numpy as np
import cvzone
from typing import List, Tuple
import config


def draw_areas(frame: np.ndarray) -> np.ndarray:
    """
    Рисует области подсчета на кадре
    
    Args:
        frame: Входной кадр
        
    Returns:
        np.ndarray: Кадр с нарисованными областями
    """
    area1 = np.array(config.AREA_1, np.int32)
    area2 = np.array(config.AREA_2, np.int32)
    cv2.polylines(frame, [area1], True, config.COLOR_GREEN, config.LINE_THICKNESS)
    cv2.polylines(frame, [area2], True, config.COLOR_GREEN, config.LINE_THICKNESS)
    return frame


def draw_objects(frame: np.ndarray, objects_bbs_ids: List[List[int]], 
                 counter: 'PeopleCounter') -> np.ndarray:
    """
    Рисует обнаруженные объекты на кадре
    
    Args:
        frame: Входной кадр
        objects_bbs_ids: Список объектов в формате [x1, y1, x2, y2, id]
        counter: Экземпляр счетчика для проверки статуса объектов
        
    Returns:
        np.ndarray: Кадр с нарисованными объектами
    """
    for bbox in objects_bbs_ids:
        x1, y1, x2, y2, obj_id = bbox
        center_x = (x1 + x2) // 2
        center_y = y2
        
        # Рисуем объекты, которые пересекают зоны и засчитываются
        # Белый прямоугольник для вышедших (из area2 в area1)
        if obj_id in counter.going_out:
            if cv2.pointPolygonTest(counter.area1, (center_x, center_y), False) >= 0:
                cv2.circle(frame, (center_x, center_y), config.CIRCLE_RADIUS, 
                          config.COLOR_GREEN, -1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), config.COLOR_WHITE, config.LINE_THICKNESS)
                cvzone.putTextRect(frame, f'{obj_id}', (x1, y1), 1, 1)
        
        # Синий прямоугольник для вошедших (из area1 в area2)
        if obj_id in counter.going_in:
            if cv2.pointPolygonTest(counter.area2, (center_x, center_y), False) >= 0:
                cv2.circle(frame, (center_x, center_y), config.CIRCLE_RADIUS, 
                          config.COLOR_GREEN, -1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), config.COLOR_BLUE, config.LINE_THICKNESS)
                cvzone.putTextRect(frame, f'{obj_id}', (x1, y1), 1, 1)
    
    return frame


def draw_statistics(frame: np.ndarray, in_count: int, out_count: int, 
                   fps: float, device: str) -> np.ndarray:
    """
    Рисует статистику на кадре
    
    Args:
        frame: Входной кадр
        in_count: Количество вошедших
        out_count: Количество вышедших
        fps: Текущий FPS
        device: Используемое устройство
        
    Returns:
        np.ndarray: Кадр с нарисованной статистикой
    """
    cv2.putText(frame, f'In: {in_count}', config.TEXT_POSITION_IN, 
               cv2.FONT_HERSHEY_COMPLEX, config.TEXT_SCALE, config.COLOR_GREEN, 
               config.TEXT_THICKNESS)
    cv2.putText(frame, f'Out: {out_count}', config.TEXT_POSITION_OUT, 
               cv2.FONT_HERSHEY_COMPLEX, config.TEXT_SCALE, config.COLOR_RED, 
               config.TEXT_THICKNESS)
    cv2.putText(frame, f'FPS: {int(fps)}', config.TEXT_POSITION_FPS, 
               cv2.FONT_HERSHEY_COMPLEX, config.TEXT_SCALE, config.COLOR_BLUE, 
               config.TEXT_THICKNESS)
    cv2.putText(frame, f'Device: {device.upper()}', config.TEXT_POSITION_DEVICE, 
               cv2.FONT_HERSHEY_COMPLEX, 0.7, config.COLOR_YELLOW, 
               config.TEXT_THICKNESS)
    return frame


def draw_all(frame: np.ndarray, objects_bbs_ids: List[List[int]], 
            counter: 'PeopleCounter', in_count: int, out_count: int, 
            fps: float, device: str) -> np.ndarray:
    """
    Рисует все элементы визуализации на кадре
    
    Args:
        frame: Входной кадр
        objects_bbs_ids: Список объектов
        counter: Экземпляр счетчика
        in_count: Количество вошедших
        out_count: Количество вышедших
        fps: Текущий FPS
        device: Используемое устройство
        
    Returns:
        np.ndarray: Кадр с полной визуализацией
    """
    frame = draw_areas(frame)
    frame = draw_objects(frame, objects_bbs_ids, counter)
    frame = draw_statistics(frame, in_count, out_count, fps, device)
    return frame

