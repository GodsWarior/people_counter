# command_server.py
import socket
import threading
import json
import shared_data  # Импортируем общие данные


class CommandServer:
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.running = True

    def handle_client(self, conn, addr):
        print(f'Command client connected: {addr}')
        try:
            while True:
                data = conn.recv(1024).decode('utf-8').strip()
                if not data:
                    break

                print(f"Received command: {data}")

                # Обработка команд
                response = self.process_command(data)
                conn.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"Client error: {e}")
        finally:
            conn.close()
            print(f"Command client disconnected: {addr}")

    def process_command(self, command):
        """Обработка команд от клиента"""
        try:
            if command == "get_count":
                count = shared_data.get_people_count()
                return json.dumps({"status": "success", "count": count})

            elif command == "get_stats":
                stats = {
                    "count": shared_data.get_people_count(),
                    "fps": shared_data.get_fps(),
                    "status": "running"
                }
                return json.dumps({"status": "success", "data": stats})

            elif command == "restart":
                # Здесь можно добавить логику перезапуска
                return json.dumps({"status": "success", "message": "Restart command received"})

            elif command == "stop":
                self.running = False
                return json.dumps({"status": "success", "message": "Stopping command server"})

            elif command == "ping":
                return json.dumps({"status": "success", "message": "pong"})

            else:
                return json.dumps({"status": "error", "message": f"Unknown command: {command}"})

        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def start(self):
        """Запуск сервера команд"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen(5)
                print(f"🎮 Command server listening on {self.host}:{self.port}")
                print("📋 Available commands: get_count, get_stats, ping, restart, stop")

                while self.running:
                    try:
                        conn, addr = s.accept()
                        client_thread = threading.Thread(
                            target=self.handle_client,
                            args=(conn, addr),
                            daemon=True
                        )
                        client_thread.start()
                    except Exception as e:
                        if self.running:
                            print(f"Command server accept error: {e}")

        except Exception as e:
            print(f"❌ Command server failed: {e}")


def start_command_server():
    """Запуск сервера команд в отдельном потоке"""
    server = CommandServer()
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    return server_thread