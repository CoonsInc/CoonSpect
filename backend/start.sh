#!/bin/sh
alembic upgrade head
celery -A src.app.celery_app worker --loglevel=info &
uvicorn src.app.main:app --host 0.0.0.0 --port 8000
