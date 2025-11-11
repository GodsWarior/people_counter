# visualizer.py - упрощенная визуализация с одной зоной
"""
Модуль для визуализации результатов на кадре
"""
import cv2
import numpy as np
import cvzone
from typing import List, Tuple
import config


def draw_zone(frame: np.ndarray) -> np.ndarray:
    """
    Рисует зону подсчета на кадре

    Args:
        frame: Входной кадр

    Returns:
        np.ndarray: Кадр с нарисованной зоной
    """
    zone = np.array(config.COUNTING_ZONE, np.int32)
    # Рисуем полупрозрачную заливку зоны
    overlay = frame.copy()
    cv2.fillPoly(overlay, [zone], (0, 255, 0, 50))
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    # Рисуем контур зоны
    cv2.polylines(frame, [zone], True, config.COLOR_GREEN, config.LINE_THICKNESS)

    # Подпись зоны
    text_x = config.FRAME_WIDTH // 2 - 50
    text_y = config.ZONE_TOP + config.ZONE_HEIGHT // 2
    cv2.putText(frame, 'COUNTING ZONE', (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, config.COLOR_GREEN, 2)

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
        center_y = (y1 + y2) // 2

        # Проверяем статус объекта
        is_counted = obj_id in counter.total_count
        in_zone = counter.is_in_zone(obj_id)

        # Выбираем цвет в зависимости от статуса
        if is_counted:
            color = config.COLOR_WHITE  # Белый - уже подсчитан
            thickness = 3
        elif in_zone:
            color = config.COLOR_RED  # Красный - в зоне
            thickness = 2
        else:
            color = config.COLOR_BLUE  # Синий - не в зоне
            thickness = 1

        # Рисуем прямоугольник
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        # Рисуем центр объекта
        cv2.circle(frame, (center_x, center_y), config.CIRCLE_RADIUS,
                   config.COLOR_GREEN, -1)

        # ID объекта и статус
        status = "COUNTED" if is_counted else "IN ZONE" if in_zone else "TRACKING"
        cvzone.putTextRect(frame, f'ID:{obj_id} {status}', (x1, y1 - 25), 1, 1)

    return frame


def draw_statistics(frame: np.ndarray, total_count: int,
                    fps: float, device: str) -> np.ndarray:
    """
    Рисует статистику на кадре

    Args:
        frame: Входной кадр
        total_count: Общее количество людей
        fps: Текущий FPS
        device: Используемое устройство

    Returns:
        np.ndarray: Кадр с нарисованной статистикой
    """
    cv2.putText(frame, f'People Counted: {total_count}', config.TEXT_POSITION_COUNT,
                cv2.FONT_HERSHEY_COMPLEX, config.TEXT_SCALE, config.COLOR_GREEN,
                config.TEXT_THICKNESS)
    cv2.putText(frame, f'FPS: {int(fps)}', config.TEXT_POSITION_FPS,
                cv2.FONT_HERSHEY_COMPLEX, config.TEXT_SCALE, config.COLOR_BLUE,
                config.TEXT_THICKNESS)
    cv2.putText(frame, f'Device: {device.upper()}', config.TEXT_POSITION_DEVICE,
                cv2.FONT_HERSHEY_COMPLEX, 0.7, config.COLOR_YELLOW,
                config.TEXT_THICKNESS)
    return frame


def draw_all(frame: np.ndarray, objects_bbs_ids: List[List[int]],
             counter: 'PeopleCounter', total_count: int,
             fps: float, device: str) -> np.ndarray:
    """
    Рисует все элементы визуализации на кадре

    Args:
        frame: Входной кадр
        objects_bbs_ids: Список объектов
        counter: Экземпляр счетчика
        total_count: Общее количество людей
        fps: Текущий FPS
        device: Используемое устройство

    Returns:
        np.ndarray: Кадр с полной визуализацией
    """
    frame = draw_zone(frame)
    frame = draw_objects(frame, objects_bbs_ids, counter)
    frame = draw_statistics(frame, total_count, fps, device)
    return frame