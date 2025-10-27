# Я пока что не знаю зачем это нужно - Вова

from celery import Celery
import time
from config import REDIS_URL

redis_url = REDIS_URL # "redis://redis:6379/0"

celery = Celery(
    "tasks",
    broker=redis_url,
    backend=redis_url
)

# Очереди для разных типов задач
celery.conf.task_routes = {
    "stt_task": {"queue": "stt_queue"},
    "rag_task": {"queue": "rag_queue"}, 
    "llm_task": {"queue": "llm_queue"},
}

@celery.task(bind=True)
def stt_task(self, audio_file_path, task_id):
    self.update_state(
        state='PROGRESS',
        meta={'stage': 'stt', 'progress': 25, 'task_id': task_id}
    )
    
    # STT логика
    text = transcribe_audio(audio_file_path)

    return {
        'stage': 'stt_completed', 
        'text': text,
        'task_id': task_id
    }

@celery.task(bind=True)
def rag_task(self, text, task_id):
    self.update_state(
        state='PROGRESS', 
        meta={'stage': 'rag', 'progress': 50, 'task_id': task_id}
    )
    
    # RAG логика
    context = rag_search(text)

    return {
        'stage': 'rag_completed',
        'context': context,
        'task_id': task_id
    }

@celery.task(bind=True) 
def llm_task(self, text, task_id):
    self.update_state(
        state='PROGRESS', 
        meta={'stage': 'rag', 'progress': 50, 'task_id': task_id}
    )
    
    # RAG логика
    context = rag_search(text)
    
    return {
        'stage': 'rag_completed',
        'context': context,
        'task_id': task_id
    }
