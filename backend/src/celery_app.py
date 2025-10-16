from celery import Celery
import time
from config import REDIS_URL

redis_url = REDIS_URL # "redis://redis:6379/0"

app = Celery(
    'celery_app',
    broker=redis_url,        # Для очереди задач
    backend=redis_url,       # Для хранения результатов ← ЭТОГО НЕ ХВАТАЛО!
)

@app.task(name='celery_app.add_numbers')
def add_numbers(x, y):
    print(f"Worker: Calculating {x} + {y}")
    time.sleep(3)  # Имитация работы
    result = x + y
    print(f"Worker: Result is {result}")
    return result

@app.task(name='celery_app.genrep')
def generate_report(user_id):
    print(f"Worker: Generating report for user {user_id}")
    time.sleep(5)
    return f"Report for user {user_id}"

def test_celery():
    print("=== Testing Celery ===")
    
    # Проверяем подключение к Redis
    try:
        import redis
        r = redis.Redis(host='redis', port=6379, db=0)
        r.ping()
        print("✓ Redis connection: OK")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return

    # Отправляем задачу
    print("Sending task to Celery...")
    task = add_numbers.delay(10, 20)
    print(f"Task ID: {task.id}")
    print(f"Task status: {task.status}")

    # Ждем результат с таймаутом
    try:
        print("Waiting for result (max 30 seconds)...")
        result = task.get(timeout=30)
        print(f"✓ Task completed! Result: {result}")
        print(f"Final status: {task.status}")
    except Exception as e:
        print(f"✗ Task failed: {e}")
        print("Make sure Celery worker is running!")
        print("Run: celery -A src.celery_app worker --loglevel=info")

if __name__ == '__main__':
    test_celery()
