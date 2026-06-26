import redis
import json
import uuid
from celery import Celery
import os

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

celery_app = Celery('producer', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

UPLOAD_FOLDER = '/files'
FILE_TIME_LIMIT = 24 * 60 * 60

def save_file_result(task_id, result_data):
    redis_client.set(task_id, json.dumps(result_data))
    redis_client.expire(task_id, 86400)
