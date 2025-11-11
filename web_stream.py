"""
Web-сервер для стриминга видео в браузер
"""
import cv2
import threading
import time
from flask import Flask, Response
import numpy as np
import socket
import platform

app = Flask(__name__)

# Глобальные переменные
latest_frame = None
current_count = 0
current_fps = 0
frame_lock = threading.Lock()

def get_network_info(port=5000):
    """Показывает информацию о сети"""
    try:
        system = platform.system().lower()

        if system == "linux":
            try:
                result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                if result.returncode == 0:
                    local_ip = result.stdout.strip().split()[0]
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
            except:
                local_ip = "127.0.0.1"
        else:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except:
                local_ip = "127.0.0.1"

        print("=" * 60)
        print("🌐 NETWORK CONNECTION INFORMATION")
        print("=" * 60)
        print(f"📊 Local access:    http://localhost:{port}")
        print(f"🌐 Your IP access:  http://{local_ip}:{port}")
        print("=" * 60)
        print("📱 On other devices in same network:")
        print(f"   Open browser and go to: http://{local_ip}:5000")
        print("=" * 60)
        print("💡 Note: This is LOCAL access only")
        print("   For global access, use VPN or port forwarding")
        print("=" * 60)

        return local_ip
    except Exception as e:
        print(f"❌ Network info error: {e}")
        return "127.0.0.1"

def start_web_server(host='0.0.0.0', port=5000):
    """Запуск web-сервера"""
    def run_server():
        try:
            local_ip = get_network_info(port)
            print(f"🚀 Starting web server on http://{host}:{port}")
            print(f"💻 Operating System: {platform.system()}")

            # Запускаем Flask сервер
            print("✅ Starting Flask server...")
            app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)

        except Exception as e:
            print(f"❌ Web server failed: {e}")

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    return server_thread

def generate_frames():
    """Генератор видеопотока"""
    global latest_frame

    while True:
        with frame_lock:
            if latest_frame is not None:
                try:
                    ret, buffer = cv2.imencode('.jpg', latest_frame, [
                        cv2.IMWRITE_JPEG_QUALITY, 80
                    ])
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                except Exception as e:
                    print(f"Frame encoding error: {e}")
                    error_frame = np.zeros((500, 800, 3), dtype=np.uint8)
                    cv2.putText(error_frame, "STREAM ERROR", (50, 250),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    ret, buffer = cv2.imencode('.jpg', error_frame)
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.033)

@app.route('/')
def index():
    """Главная страница"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>People Counter - Live Stream</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #1a1a1a; color: white; }
            .container { max-width: 1100px; margin: 0 auto; }
            .stats { background: #2d2d2d; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .video-container { text-align: center; background: black; padding: 10px; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>People Counter - Live Monitoring</h1>
            <div class="stats">
                <strong>People Counted:</strong> <span id="count">0</span> | 
                <strong>FPS:</strong> <span id="fps">0</span> |
                <strong>Status:</strong> <span id="status">Running</span>
            </div>
            <div class="video-container">
                <img src="/video" width="1020" height="500" alt="Live Stream">
            </div>
        </div>
        <script>
            setInterval(() => {
                fetch('/stats')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('count').textContent = data.people_count;
                        document.getElementById('fps').textContent = data.fps;
                    })
                    .catch(e => console.log('Stats error:', e));
            }, 2000);
        </script>
    </body>
    </html>
    """

@app.route('/video')
def video_feed():
    """Эндпоинт для видеопотока"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def get_stats():
    """API для получения статистики"""
    global current_count, current_fps
    return {
        'people_count': current_count,
        'fps': round(current_fps, 1),
        'status': 'running'
    }

def update_stream_data(frame, people_count, fps):
    """Обновление данных для стриминга"""
    global latest_frame, current_count, current_fps

    with frame_lock:
        if frame is not None and frame.size > 0:
            latest_frame = frame.copy()
        current_count = people_count
        current_fps = fps