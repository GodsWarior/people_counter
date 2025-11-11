# shared_data.py
"""
Общие данные для всего приложения
"""

# Глобальные объекты которые будут доступны всем модулям
counter_obj = None
web_stream = None
tracker_obj = None

def initialize_shared_data(counter, web_stream_ref, tracker):
    """Инициализация общих данных"""
    global counter_obj, web_stream, tracker_obj
    counter_obj = counter
    web_stream = web_stream_ref
    tracker_obj = tracker

def get_people_count():
    """Безопасное получение количества людей"""
    global counter_obj
    return counter_obj.get_count() if counter_obj else 0

def get_fps():
    """Безопасное получение FPS"""
    global web_stream
    return getattr(web_stream, 'current_fps', 0) if web_stream else 0