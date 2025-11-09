"""
Модуль для детекции объектов на кадре
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
import device_manager
import config


def detect_people(frame: np.ndarray, model: YOLO, device: str, 
                  class_list: List[str]) -> List[List[int]]:
    """
    Обнаруживает людей на кадре
    
    Args:
        frame: Входной кадр
        model: YOLO модель
        device: Устройство для вычислений
        class_list: Список классов COCO
        
    Returns:
        List[List[int]]: Список обнаруженных объектов в формате [x1, y1, x2, y2]
    """
    # Изменяем размер кадра
    resized_frame = cv2.resize(frame, config.RESIZE_FACTOR)
    
    # Преобразуем device для YOLO
    yolo_device = device_manager.get_yolo_device(device)
    
    # Выполняем детекцию
    results = model.predict(resized_frame, verbose=False, device=yolo_device, half=False)
    
    # Извлекаем обнаруженные объекты
    detected_objects = extract_objects(results, class_list)
    
    return detected_objects, resized_frame


def extract_objects(results, class_list: List[str]) -> List[List[int]]:
    """
    Извлекает объекты из результатов YOLO
    
    Args:
        results: Результаты YOLO predict
        class_list: Список классов COCO
        
    Returns:
        List[List[int]]: Список боксов в формате [x1, y1, x2, y2]
    """
    detected_objects = []
    
    if results and len(results) > 0:
        result = results[0]
        
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xyxy.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = map(int, box)
                class_id = int(classes[i])
                confidence = confidences[i]
                
                if is_person(class_id, confidence, class_list):
                    detected_objects.append([x1, y1, x2, y2])
    
    return detected_objects


def is_person(class_id: int, confidence: float, class_list: List[str]) -> bool:
    """
    Проверяет, является ли обнаруженный объект человеком
    
    Args:
        class_id: ID класса
        confidence: Уровень уверенности
        class_list: Список классов COCO
        
    Returns:
        bool: True если объект - человек с достаточной уверенностью
    """
    if class_id >= len(class_list):
        return False
    
    class_name = class_list[class_id]
    is_person_class = config.TARGET_CLASS in class_name.lower()
    has_sufficient_confidence = confidence > config.CONFIDENCE_THRESHOLD
    
    return is_person_class and has_sufficient_confidence

