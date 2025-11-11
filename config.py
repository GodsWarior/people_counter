# config.py - упрощенные настройки
"""
Конфигурационный файл с настройками проекта
"""
from typing import List, Tuple

# Пути к файлам
MODEL_PATH = 'yolov8s.pt'
VIDEO_PATH = 'rtsp://view:Bdea6Esd7BaiKC4@95.143.14.21:13554/Streaming/Channels/101'
CLASS_LIST_PATH = 'coco.txt'

# Параметры обработки видео
FRAME_WIDTH = 1020
FRAME_HEIGHT = 500
RESIZE_FACTOR = (FRAME_WIDTH, FRAME_HEIGHT)

# Параметры детекции
CONFIDENCE_THRESHOLD = 0.5
TARGET_CLASS = 'person'

# Одна горизонтальная зона по центру экрана
# Формат: [(левый_верхний), (правый_верхний), (правый_нижний), (левый_нижний)]
ZONE_HEIGHT = 100  # Высота зоны в пикселях
ZONE_TOP = (FRAME_HEIGHT - ZONE_HEIGHT) // 2
ZONE_BOTTOM = ZONE_TOP + ZONE_HEIGHT

COUNTING_ZONE: List[Tuple[int, int]] = [
    (0, ZONE_TOP),                    # Левый верхний
    (FRAME_WIDTH, ZONE_TOP),          # Правый верхний
    (FRAME_WIDTH, ZONE_BOTTOM),       # Правый нижний
    (0, ZONE_BOTTOM)                  # Левый нижний
]

# Параметры трекера
TRACKER_DISTANCE_THRESHOLD = 35

# Параметры FPS
FPS_WINDOW_SIZE = 30
LOG_INTERVAL = 30  # Логировать каждые N кадров

# Параметры отрисовки
LINE_THICKNESS = 2
CIRCLE_RADIUS = 4
TEXT_SCALE = 1
TEXT_THICKNESS = 2

# Цвета (BGR)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (255, 255, 0)

# Позиции текста на экране
TEXT_POSITION_COUNT = (20, 50)  # Позиция для общего счетчика
TEXT_POSITION_FPS = (20, 100)
TEXT_POSITION_DEVICE = (20, 150)

# Название окна
WINDOW_NAME = 'people_counter'