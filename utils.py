"""
Вспомогательные функции
"""
from typing import List


def load_class_list(file_path: str) -> List[str]:
    """
    Загружает список классов из файла
    
    Args:
        file_path: Путь к файлу со списком классов
        
    Returns:
        List[str]: Список классов
    """
    with open(file_path, "r", encoding='utf-8') as file:
        return file.read().strip().split("\n")


def mouse_callback(event, x, y, flags, param):
    """
    Callback функция для обработки событий мыши
    Используется для отладки координат
    
    Args:
        event: Тип события мыши
        x: Координата X
        y: Координата Y
        flags: Флаги события
        param: Дополнительные параметры
    """
    if event == 0:  # cv2.EVENT_MOUSEMOVE
        print(f"Mouse position: [{x}, {y}]")

