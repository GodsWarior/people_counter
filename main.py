"""
Основной файл для запуска системы подсчета людей
"""
import cv2
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
        Tuple: (обработанный кадр, количество вышедших, количество вошедших)
    """
    # Детекция объектов
    detected_objects, resized_frame = detector.detect_people(
        frame, model, device, class_list
    )
    
    # Трекинг объектов
    objects_bbs_ids = tracker_obj.update(detected_objects)
    
    # Подсчет людей
    out_count, in_count = counter_obj.update(objects_bbs_ids)
    
    return resized_frame, objects_bbs_ids, out_count, in_count


def setup_window():
    """Настраивает окно OpenCV"""
    cv2.namedWindow(config.WINDOW_NAME)
    cv2.setMouseCallback(config.WINDOW_NAME, utils.mouse_callback)


def main():
    """Основная функция"""
    # Инициализация устройства
    device, device_info = device_manager.get_device()
    
    # Настройка окна
    setup_window()
    
    # Загрузка модели
    model = model_loader.load_model(config.MODEL_PATH, device)
    if model is None:
        return
    
    # Открытие видео
    cap = cv2.VideoCapture(config.VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: Could not open video stream: {config.VIDEO_PATH}")
        return
    
    # Загрузка классов и инициализация компонентов
    class_list = utils.load_class_list(config.CLASS_LIST_PATH)
    tracker_obj = tracker.Tracker()
    counter_obj = counter.PeopleCounter(config.AREA_1, config.AREA_2)
    fps_calculator_obj = fps_calculator.FPSCalculator(config.FPS_WINDOW_SIZE)
    
    frame_count = 0
    
    print("\nStarting video processing...")
    print("Press ESC to exit\n")
    
    # Основной цикл обработки
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video or error reading frame.")
            break
        
        frame_count += 1
        
        # Расчет FPS
        avg_fps = fps_calculator_obj.update()
        
        # Обработка кадра
        processed_frame, objects_bbs_ids, out_count, in_count = process_frame(
            frame, model, class_list, tracker_obj, counter_obj, device
        )
        
        # Визуализация
        processed_frame = visualizer.draw_all(
            processed_frame, objects_bbs_ids, counter_obj, 
            in_count, out_count, avg_fps, device
        )
        
        # Логирование
        if frame_count % config.LOG_INTERVAL == 0:
            print(f"Frame: {frame_count}, FPS: {avg_fps:.1f}, "
                  f"In: {in_count}, Out: {out_count}, Device: {device}")
        
        # Отображение
        cv2.imshow(config.WINDOW_NAME, processed_frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC для выхода
            break
    
    # Очистка ресурсов
    cap.release()
    cv2.destroyAllWindows()
    print("\nProcessing completed.")


if __name__ == "__main__":
    main()
