"""
Конфигурационный файл с настройками проекта
"""
from typing import List, Tuple

# Пути к файлам
MODEL_PATH = 'yolov8s.pt'
VIDEO_PATH = 'video/p.mp4'
CLASS_LIST_PATH = 'coco.txt'

# Параметры обработки видео
FRAME_WIDTH = 1020
FRAME_HEIGHT = 500
RESIZE_FACTOR = (FRAME_WIDTH, FRAME_HEIGHT)

# Параметры детекции
CONFIDENCE_THRESHOLD = 0.5
TARGET_CLASS = 'person'

# Области для подсчета (координаты полигонов)
AREA_1: List[Tuple[int, int]] = [(494, 289), (505, 499), (578, 496), (530, 292)]
AREA_2: List[Tuple[int, int]] = [(548, 290), (600, 496), (637, 493), (574, 288)]

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
TEXT_POSITION_IN = (20, 50)
TEXT_POSITION_OUT = (20, 100)
TEXT_POSITION_FPS = (20, 150)
TEXT_POSITION_DEVICE = (20, 200)

# Название окна
WINDOW_NAME = 'people_counter'

