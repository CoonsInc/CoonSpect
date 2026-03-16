import asyncio
import json
import requests
from typing import Optional, Dict, Any, BinaryIO
import threading
import time
import os

# Синхронный HTTP клиент
class SyncHTTPClient:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.session = requests.Session()
        
    def get(self, endpoint: str, params: Optional[Dict] = None, 
            headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Отправка GET запроса (синхронно)"""
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json()
        else:
            return {"text": response.text}
            
    def post(self, endpoint: str, data: Optional[Dict] = None,
             json_data: Optional[Dict] = None, 
             files: Optional[Dict] = None,
             headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Отправка POST запроса (синхронно) с поддержкой файлов"""
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(
            url, 
            data=data, 
            json=json_data, 
            files=files,
            headers=headers
        )
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json()
        else:
            return {"text": response.text}
            
    def close(self):
        """Закрытие сессии"""
        self.session.close()


# Асинхронный WebSocket клиент
class AsyncWebSocketClient:
    def __init__(self, url: str, on_message=None, on_error=None, on_close=None):
        self.url = url
        self.websocket = None
        self.running = False
        self.loop = None
        self.thread = None
        
        # Callback-функции
        self.on_message = on_message or (lambda msg: print(f"WebSocket сообщение: {msg}"))
        self.on_error = on_error or (lambda err: print(f"WebSocket ошибка: {err}"))
        self.on_close = on_close or (lambda: print("WebSocket соединение закрыто"))
        
    async def _connect_async(self):
        """Асинхронное подключение и обработка сообщений"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(self.url) as websocket:
                    self.websocket = websocket
                    print(f"WebSocket подключен к {self.url}")
                    
                    async for msg in websocket:
                        if not self.running:
                            break
                            
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            self.on_message(msg.data)
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            self.on_error(websocket.exception())
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                            
        except Exception as e:
            self.on_error(str(e))
        finally:
            self.on_close()
            self.running = False
    
    def _run_async(self):
        """Запуск асинхронного event loop в отдельном потоке"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect_async())
    
    def connect(self):
        """Запуск WebSocket соединения в фоновом потоке"""
        if self.running:
            print("WebSocket уже запущен")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_async, daemon=True)
        self.thread.start()
        
        # Ждем немного для установки соединения
        time.sleep(0.5)
    
    async def send_async(self, message: str):
        """Асинхронная отправка сообщения"""
        if self.websocket and not self.websocket.closed:
            await self.websocket.send_str(message)
            print(f"Отправлено через WebSocket: {message}")
    
    def send(self, message: str):
        """Синхронная отправка сообщения (запускает корутину в event loop)"""
        if self.loop and self.running:
            asyncio.run_coroutine_threadsafe(self.send_async(message), self.loop)
    
    def close(self):
        """Закрытие WebSocket соединения"""
        self.running = False
        if self.thread:
            # Ждем завершения потока (но не бесконечно)
            self.thread.join(timeout=2.0)


# Утилиты для работы с файлами
def validate_audio_file(filepath: str) -> bool:
    """Проверка существования файла и его расширения"""
    if not os.path.exists(filepath):
        print(f"Файл не найден: {filepath}")
        return False
    
    # Проверяем расширение аудио файла
    valid_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
    file_ext = os.path.splitext(filepath)[1].lower()
    
    if file_ext not in valid_extensions:
        print(f"Неподдерживаемый формат файла: {file_ext}")
        print(f"Поддерживаемые форматы: {', '.join(valid_extensions)}")
        return False
    
    return True


def get_file_size_mb(filepath: str) -> float:
    """Получение размера файла в мегабайтах"""
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)


# Основные функции
def create_task() -> str:
    """Создание задачи (синхронно)"""
    client = SyncHTTPClient(base_url="http://localhost:8000")
    try:
        response = client.get("/task/create")
        task_id = response.get("msg")
        if task_id:
            print(f"Создана задача с ID: {task_id}")
        else:
            print(f"Неожиданный ответ от сервера: {response}")
        return task_id
    except requests.exceptions.ConnectionError:
        print("Ошибка подключения к серверу. Убедитесь, что сервер запущен на http://localhost:8000")
        return None
    except Exception as e:
        print(f"Ошибка при создании задачи: {e}")
        return None
    finally:
        client.close()


def start_task(task_id: str, audio_file_path: str):
    """Запуск задачи с загрузкой аудио файла (синхронно)"""
    if not task_id:
        print("Ошибка: не указан ID задачи")
        return None
    
    client = SyncHTTPClient(base_url="http://localhost:8000")
    
    try:
        # Подготавливаем файл для отправки
        file_size_mb = get_file_size_mb(audio_file_path)
        print(f"Подготовка файла к загрузке: {audio_file_path}")
        print(f"Размер файла: {file_size_mb:.2f} MB")
        
        # Открываем файл в бинарном режиме
        with open(audio_file_path, 'rb') as audio_file:
            # Создаем словарь с файлом для отправки
            files = {
                'file': (
                    os.path.basename(audio_file_path),  # Имя файла
                    audio_file,                         # Файловый объект
                    f'audio/{os.path.splitext(audio_file_path)[1][1:]}'  # MIME тип
                )
            }
            
            # Дополнительные данные формы (если нужны)
            data = {
                'task_id': task_id,
                'filename': os.path.basename(audio_file_path),
                'filesize': f"{file_size_mb:.2f}MB"
            }
            
            print(f"Отправка файла на сервер...")
            
            # Отправляем POST запрос с файлом
            response = client.post(
                f"/task/start/{task_id}", 
                data=data,
                files=files
            )
            
            print(f"Файл успешно загружен!")
            print(f"Ответ сервера: {response}")
            return response
            
    except FileNotFoundError:
        print(f"Ошибка: файл не найден - {audio_file_path}")
        return None
    except requests.exceptions.ConnectionError:
        print("Ошибка подключения к серверу при отправке файла")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP запроса: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None
    finally:
        client.close()


def task_status_listener(task_id: str):
    """Прослушивание статуса задачи через WebSocket"""
    if not task_id:
        print("Ошибка: не указан ID задачи для WebSocket")
        return None
    
    ws_url = f"ws://localhost:8000/task/ws/{task_id}"
    
    # Кастомные обработчики событий WebSocket
    def on_message(msg):
        print(f"Статус задачи {task_id}: {msg}")
    
    def on_error(err):
        print(f"⚠️ Ошибка WebSocket для задачи {task_id}: {err}")
    
    def on_close():
        print(f"🔌 Соединение WebSocket для задачи {task_id} закрыто")
    
    # Создаем и запускаем WebSocket клиент
    ws_client = AsyncWebSocketClient(
        ws_url, 
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws_client.connect()
    return ws_client


def check_task_status(task_id: str):
    """Проверка статуса задачи через HTTP (синхронно)"""
    if not task_id:
        return None
    
    client = SyncHTTPClient(base_url="http://localhost:8000")
    try:
        response = client.get(f"/task/status/{task_id}")
        print(f"Текущий статус задачи: {response}")
        return response
    except Exception as e:
        print(f"Ошибка проверки статуса: {e}")
        return None
    finally:
        client.close()


def main():
    """Основная функция с примером использования"""
    
    print("=" * 50)
    print("Загрузчик аудио файлов с WebSocket мониторингом")
    print("=" * 50)
    
    # 1. Создаем задачу (синхронно)
    print("\n1. Создание новой задачи...")
    task_id = create_task()
    
    if not task_id:
        print("Не удалось создать задачу. Завершение работы.")
        return
    
    # 2. Запускаем слушатель статуса в фоне (WebSocket)
    print(f"\n2. Запуск WebSocket мониторинга для задачи {task_id}...")
    ws_client = task_status_listener(task_id)
    
    if not ws_client:
        print("Не удалось запустить WebSocket мониторинг")
        return
    
    # 3. Ждем немного, чтобы WebSocket успел подключиться
    print("Ожидание подключения WebSocket...")
    time.sleep(2)
    
    # 4. Запускаем задачу с аудио файлом
    print(f"\n3. Запуск обработки аудио файла...")
    
    # Пример пути к файлу - можно заменить на реальный путь
    audio_file = input("Введите путь к аудио файлу: ").strip()
    
    # Если файл не указан, используем тестовый (закомментируйте для реального использования)
    if not audio_file or not os.path.exists(audio_file):
        print(f"Тестовый файл не найден: {audio_file}")
        ws_client.close()
        return
    
    # Запускаем задачу с файлом
    result = start_task(task_id, audio_file)
    
    if not result:
        print("Не удалось запустить задачу")
        ws_client.close()
        return
    
    # 5. Основной поток продолжает работать
    try:
        print("\n4. Основной поток работает. Нажмите Ctrl+C для выхода.")
        print("WebSocket работает в фоне и получает сообщения...")
        print("=" * 50)
        
        # Имитация работы основного приложения
        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            
            # Пример: периодическая проверка через HTTP (синхронно)
            if counter % 10 == 0:
                print(f"\n[{counter} сек.] Проверка статуса через HTTP...")
                check_task_status(task_id)
                
            # Отправка тестового сообщения через WebSocket каждые 15 секунд
            if counter % 15 == 0 and ws_client:
                print(f"[{counter} сек.] Отправка ping через WebSocket...")
                ws_client.send(json.dumps({"action": "ping", "timestamp": time.time()}))
                
    except KeyboardInterrupt:
        print("\n\nЗавершение работы по запросу пользователя...")
    finally:
        # Закрываем WebSocket соединение
        print("\n5. Закрытие соединений...")
        ws_client.close()
        
        # Финальная проверка статуса
        print("\nФинальный статус задачи:")
        check_task_status(task_id)
        
        print("\nПрограмма завершена.")
        print("=" * 50)


# Альтернативный простой пример использования
def simple_example():
    """Простой пример использования без интерактивного ввода"""
    
    # Путь к аудио файлу (замените на реальный)
    audio_file_path = "example.wav"
    
    if not os.path.exists(audio_file_path):
        print(f"Файл не найден: {audio_file_path}")
        print("Создайте тестовый файл или укажите правильный путь.")
        return
    
    # 1. Создаем задачу
    task_id = create_task()
    if not task_id:
        return
    
    # 2. Запускаем WebSocket слушатель
    ws_client = task_status_listener(task_id)
    time.sleep(1)
    
    # 3. Запускаем задачу с файлом
    start_task(task_id, audio_file_path)
    
    # 4. Ждем завершения (например, 30 секунд)
    print("Ожидание завершения обработки...")
    time.sleep(30)
    
    # 5. Закрываем соединение
    ws_client.close()


if __name__ == "__main__":
    # Запускаем основной пример
    main()
    
    # Или простой пример (раскомментируйте нужное)
    # simple_example()