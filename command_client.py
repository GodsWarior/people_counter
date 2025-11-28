# command_client.py
import socket
import json


class PeopleCounterClient:
    def __init__(self, host, port=65432):
        self.host = host
        self.port = port

    def send_command(self, command):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)  # Таймаут 10 секунд
                s.connect((self.host, self.port))
                s.sendall(command.encode('utf-8'))

                response = s.recv(1024).decode('utf-8')
                return json.loads(response)

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_people_count(self):
        return self.send_command("get_count")

    def get_stats(self):
        return self.send_command("get_stats")

    def restart_server(self):
        return self.send_command("restart")


# Пример использования
if __name__ == "__main__":
    # Укажи реальный IP сервера
    client = PeopleCounterClient("192.168.1.100", 65432)

    # Получить количество людей
    result = client.get_people_count()
    print(f"People count: {result}")

    # Получить полную статистику
    stats = client.get_stats()
    print(f"Stats: {stats}")