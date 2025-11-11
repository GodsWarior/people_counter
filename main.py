# main.py - добавь эти изменения
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
import web_stream

# ✅ ДОБАВЬ ЭТОТ ИМПОРТ
import shared_data
import command_server  # Теперь без циклического импорта


def process_frame(frame, model, class_list, tracker_obj, counter_obj, device):
    """Обрабатывает один кадр"""
    # ... твой существующий код без изменений ...
    if frame is None or frame.size == 0:
        return None, [], 0

    detected_objects, resized_frame = detector.detect_people(
        frame, model, device, class_list
    )

    objects_bbs_ids = tracker_obj.update(detected_objects)
    total_count = counter_obj.update(objects_bbs_ids)

    return resized_frame, objects_bbs_ids, total_count


def main():
    """Основная функция"""
    print("🚀 Starting People Counter with Web Stream and Command Server...")

    # Определяем устройство
    device, device_info = device_manager.get_device()

    # Запускаем web-сервер
    web_thread = web_stream.start_web_server()
    print("✓ Web server started in background thread")

    # ✅ ИНИЦИАЛИЗИРУЕМ ОБЩИЕ ДАННЫЕ ПОСЛЕ СОЗДАНИЯ ОБЪЕКТОВ
    # Сначала создаем все объекты
    model = model_loader.load_model(config.MODEL_PATH, device)
    if model is None:
        print("❌ Failed to load model. Exiting.")
        return

    class_list = utils.load_class_list(config.CLASS_LIST_PATH)
    tracker_obj = tracker.Tracker()
    counter_obj = counter.PeopleCounter(config.COUNTING_ZONE)
    fps_calculator_obj = fps_calculator.FPSCalculator(config.FPS_WINDOW_SIZE)

    # ✅ ТЕПЕРЬ инициализируем общие данные
    shared_data.initialize_shared_data(counter_obj, web_stream, tracker_obj)
    print("✓ Shared data initialized")

    # ✅ ЗАПУСКАЕМ СЕРВЕР КОМАНД
    command_thread = command_server.start_command_server()
    print("✓ Command server started on port 65432")

    # Инициализация камеры
    cap = cv2.VideoCapture(config.VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video stream: {config.VIDEO_PATH}")
        return

    frame_count = 0
    error_count = 0
    max_errors = 10

    print("\n🎥 Starting video processing...")
    print("📊 Web interface available at: http://0.0.0.0:5000")
    print("🎮 Command server available at: port 65432")
    print("⏹️  Press Ctrl+C to exit\n")

    # Основной цикл обработки
    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                error_count += 1
                print(f"⚠️  Error reading frame {error_count}/{max_errors}")

                if error_count >= max_errors:
                    print("🔁 Too many errors. Attempting to reconnect...")
                    cap.release()
                    time.sleep(3)
                    cap = cv2.VideoCapture(config.VIDEO_PATH)

                    if not cap.isOpened():
                        print("❌ Failed to reconnect. Exiting.")
                        break
                    error_count = 0
                continue

            error_count = 0
            frame_count += 1

            # Расчет FPS
            avg_fps = fps_calculator_obj.update()

            # Обработка кадра
            processed_frame, objects_bbs_ids, total_count = process_frame(
                frame, model, class_list, tracker_obj, counter_obj, device
            )

            if processed_frame is None:
                processed_frame = cv2.resize(frame, config.RESIZE_FACTOR)

            # Визуализация
            processed_frame = visualizer.draw_all(
                processed_frame, objects_bbs_ids, counter_obj,
                total_count, avg_fps, device
            )

            # Обновляем данные для web-стрима
            web_stream.update_stream_data(processed_frame, total_count, avg_fps)

            # Логирование
            if frame_count % config.LOG_INTERVAL == 0:
                print(f"📊 Frame: {frame_count}, FPS: {avg_fps:.1f}, "
                      f"Total: {total_count}, Device: {device}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n🛑 Stopping by user request...")

    # Очистка ресурсов
    cap.release()
    cv2.destroyAllWindows()
    final_count = counter_obj.get_count()
    print(f"\n✅ Processing completed. Total people counted: {final_count}")
    print(f"🌐 Web server: http://0.0.0.0:5000")
    print(f"🎮 Command server: port 65432")
    print("💡 Press Ctrl+C to stop all servers")


if __name__ == "__main__":
    main()