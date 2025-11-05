#!/bin/sh

# Запускаем миграции
# alembic upgrade head

# Запускаем celery worker в фоне
# celery -A src.celery_app worker --loglevel=info &

# Запускаем uvicorn (последняя команда - она будет основной процесс)
uvicorn src.main:app --host 0.0.0.0 --port 8000
