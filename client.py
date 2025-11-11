# client_public.py
import requests
import os
import json


class GlobalPhotoUploader:
    def __init__(self):
        self.server_url = None

    def set_server(self, server_url):
        """Установить адрес сервера"""
        if not server_url.startswith(('http://', 'https://')):
            server_url = 'http://' + server_url
        self.server_url = server_url.rstrip('/')

    def check_server(self):
        """Проверить доступность сервера"""
        if not self.server_url:
            print("❌ Адрес сервера не установлен")
            return False

        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            if response.status_code == 200:
                info = response.json()
                print(f"✅ Сервер доступен: {info['status']}")
                print(f"📍 IP сервера: {info.get('server_ip', 'unknown')}")
                return True
            else:
                print("❌ Сервер недоступен")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Не удалось подключиться к серверу: {self.server_url}")
            return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def upload_file(self, file_path, description=""):
        """Отправить файл на сервер"""
        if not self.check_server():
            return False

        try:
            if not os.path.exists(file_path):
                print(f"❌ Файл не найден: {file_path}")
                return False

            # Определяем MIME тип
            ext = os.path.splitext(file_path)[1].lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')

            # Отправляем файл
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, mime_type)}
                data = {'description': description}

                print(f"📤 Отправка {os.path.basename(file_path)} на сервер...")
                response = requests.post(
                    f"{self.server_url}/upload",
                    files=files,
                    data=data,
                    timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                print("✅ Фото успешно отправлено!")
                print(f"📁 Имя файла: {result['filename']}")
                print(f"📝 Описание: {result['description']}")
                print(f"📏 Размер: {result['size']} bytes")
                print(f"🔗 Ссылка для скачивания: {self.server_url}{result['download_url']}")
                return True
            else:
                error = response.json()
                print(f"❌ Ошибка сервера: {error.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Ошибка при отправке: {e}")
            return False

    def list_files(self):
        """Показать файлы на сервере"""
        if not self.check_server():
            return False

        try:
            response = requests.get(f"{self.server_url}/files", timeout=10)
            if response.status_code == 200:
                data = response.json()
                files = data.get('files', [])

                if files:
                    print(f"\n📁 Файлы на сервере ({len(files)}):")
                    for file in files:
                        print(f"  📄 {file['filename']} ({file['size']} bytes)")
                else:
                    print("📁 На сервере нет файлов")
                return True
            else:
                print("❌ Не удалось получить список файлов")
                return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False


def main():
    uploader = GlobalPhotoUploader()

    print("🌐 ГЛОБАЛЬНАЯ ОТПРАВКА ФОТО")
    print("=" * 40)

    # Запрос адреса сервера
    server_url = input("Введите адрес сервера (IP или домен): ").strip()
    uploader.set_server(server_url)

    while True:
        print("\n" + "=" * 40)
        print("1. 📤 Отправить фото")
        print("2. 📁 Показать файлы на сервере")
        print("3. 🔄 Сменить сервер")
        print("4. 🚪 Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            file_path = input("Введите путь к файлу: ").strip().strip('"')
            description = input("Введите описание: ")
            uploader.upload_file(file_path, description)

        elif choice == "2":
            uploader.list_files()

        elif choice == "3":
            new_server = input("Введите новый адрес сервера: ").strip()
            uploader.set_server(new_server)
            uploader.check_server()

        elif choice == "4":
            print("👋 До свидания!")
            break

        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    main()