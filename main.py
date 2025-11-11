# main.py - с улучшенной обработкой ошибок видео потока
"""
Основной файл для запуска системы подсчета людей
"""
import cv2
import time

import numpy as np

import config
import device_manager
import model_loader
import detector
import tracker
import counter
import visualizer
import fps_calculator
import utils


def process_frame(frame, model, class_list, tracker_obj, counter_obj, device):
    """
    Обрабатывает один кадр: детекция, трекинг, подсчет

    Args:
        frame: Входной кадр
        model: YOLO модель
        class_list: Список классов COCO
        tracker_obj: Экземпляр трекера
        counter_obj: Экземпляр счетчика
        device: Устройство для вычислений

    Returns:
        Tuple: (обработанный кадр, количество людей)
    """
    # Проверяем валидность кадра
    if frame is None or frame.size == 0:
        return None, [], 0

    # Детекция объектов
    detected_objects, resized_frame = detector.detect_people(
        frame, model, device, class_list
    )

    # Трекинг объектов
    objects_bbs_ids = tracker_obj.update(detected_objects)

    # Подсчет людей
    total_count = counter_obj.update(objects_bbs_ids)

    return resized_frame, objects_bbs_ids, total_count


def setup_window():
    """Настраивает окно OpenCV"""
    cv2.namedWindow(config.WINDOW_NAME)
    cv2.setMouseCallback(config.WINDOW_NAME, utils.mouse_callback)


def create_blank_frame():
    """Создает пустой кадр с сообщением об ошибке"""
    blank_frame = np.zeros((500, 1020, 3), dtype=np.uint8)
    cv2.putText(blank_frame, "WAITING FOR VIDEO STREAM...",
                (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(blank_frame, "Trying to reconnect...",
                (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    return blank_frame


def initialize_camera():
    """Инициализирует камеру с улучшенными параметрами"""
    cap = cv2.VideoCapture(config.VIDEO_PATH)

    # Устанавливаем параметры для лучшей стабильности RTSP
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))

    # Даем камере время на инициализацию
    time.sleep(2)

    return cap


def main():
    """Основная функция"""
    import numpy as np

    device, device_info = device_manager.get_device()

    # Настройка окна
    setup_window()

    # Загрузка модели
    model = model_loader.load_model(config.MODEL_PATH, device)
    if model is None:
        return

    # Инициализация камеры
    cap = initialize_camera()
    if not cap.isOpened():
        print(f"Error: Could not open video stream: {config.VIDEO_PATH}")
        return

    # Загрузка классов и инициализация компонентов
    class_list = utils.load_class_list(config.CLASS_LIST_PATH)
    tracker_obj = tracker.Tracker()
    counter_obj = counter.PeopleCounter(config.COUNTING_ZONE)
    fps_calculator_obj = fps_calculator.FPSCalculator(config.FPS_WINDOW_SIZE)

    frame_count = 0
    error_count = 0
    max_errors = 10

    print("\nStarting video processing...")
    print("Press ESC to exit\n")

    # Основной цикл обработки
    while True:
        ret, frame = cap.read()

        if not ret:
            error_count += 1
            print(f"Error reading frame {error_count}/{max_errors}")

            if error_count >= max_errors:
                print("Too many errors. Attempting to reconnect...")
                cap.release()
                time.sleep(3)  # Ждем перед переподключением
                cap = initialize_camera()

                if not cap.isOpened():
                    print("Failed to reconnect. Exiting.")
                    break

                error_count = 0
                continue

            # Показываем пустой кадр с сообщением
            blank_frame = create_blank_frame()
            cv2.imshow(config.WINDOW_NAME, blank_frame)

            if cv2.waitKey(100) & 0xFF == 27:  # ESC для выхода
                break
            continue

        # Сброс счетчика ошибок при успешном чтении
        error_count = 0

        frame_count += 1

        # Расчет FPS
        avg_fps = fps_calculator_obj.update()

        # Обработка кадра
        processed_frame, objects_bbs_ids, total_count = process_frame(
            frame, model, class_list, tracker_obj, counter_obj, device
        )

        # Если обработка не удалась, используем оригинальный кадр
        if processed_frame is None:
            processed_frame = cv2.resize(frame, config.RESIZE_FACTOR)

        # Визуализация
        processed_frame = visualizer.draw_all(
            processed_frame, objects_bbs_ids, counter_obj,
            total_count, avg_fps, device
        )

        # Логирование
        if frame_count % config.LOG_INTERVAL == 0:
            print(f"Frame: {frame_count}, FPS: {avg_fps:.1f}, "
                  f"Total: {total_count}, Device: {device}")

        # Отображение
        cv2.imshow(config.WINDOW_NAME, processed_frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC для выхода
            break

    # Очистка ресурсов
    cap.release()
    cv2.destroyAllWindows()
    print(f"\nProcessing completed. Total people counted: {counter_obj.get_count()}")


if __name__ == "__main__":
    main()