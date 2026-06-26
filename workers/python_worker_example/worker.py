import time
import uuid
from celery import Celery
import os

# Конфигурация Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/1')

# Создание Celery приложения
celery_app = Celery('python_worker', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# Настройка Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

@celery_app.task(name='workers.math_task')
def process_math_task(task_data):
    """
    Обработка математических задач
    """
    print(f"Processing math task: {task_data}")

    # Имитация длительной обработки
    time.sleep(10)

    # Удваиваем значение
    task_data['value'] *= 2
    task_data['status'] = 'completed'

    print(f"Math task {task_data.get('task_id', 'unknown')} completed")
    return task_data

if __name__ == '__main__':
    # Запуск Celery воркера
    celery_app.start()