import redis
import json
import uuid
from celery import Celery
import os

# Конфигурация Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Создание Celery приложения
celery_app = Celery('middleware', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# Настройка Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Redis клиент для хранения файлов (остается как есть)
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Конфигурация для файлов
UPLOAD_FOLDER = '/files'
FILE_TIME_LIMIT = 24 * 60 * 60  # 24 часа

def save_file_result(task_id, result_data):
    """
    Сохраняет результат выполнения задачи в Redis
    """
    redis_client.set(task_id, json.dumps(result_data))
    redis_client.expire(task_id, 86400)  # Хранение результата 1 день