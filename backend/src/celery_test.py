from celery_app import celery

@celery.task() 
def add_numbers(x, y):
    return x + y

def test_celery():
    print("=== Testing Celery ===")
    
    # Проверяем подключение к Redis
    try:
        import redis
        r = redis.Redis(host="redis", port=6379, db=0)
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
        print("Run: celery -A src.celery_test worker --loglevel=info")

if __name__ == "__main__":
    test_celery()