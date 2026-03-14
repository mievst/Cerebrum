import subprocess
import json
import os
from celery import Celery

# Конфигурация Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Создание Celery приложения
celery_app = Celery('rust_worker', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

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

@celery_app.task(name='workers.rust_math_task')
def process_rust_math_task(task_data):
    """
    Обработка математических задач Rust через subprocess
    """
    print(f"Processing Rust math task: {task_data}")

    try:
        # Преобразуем данные задачи в JSON строку
        task_json = json.dumps(task_data)

        # Вызываем Rust приложение через subprocess
        result = subprocess.run(
            ['./target/release/rust_worker', task_json],
            cwd='/app',
            capture_output=True,
            text=True,
            timeout=300  # 5 минут таймаут
        )

        # Проверяем код возврата
        if result.returncode != 0:
            raise Exception(f"Rust application failed with return code {result.returncode}: {result.stderr}")

        # Парсим результат из stdout
        result_data = json.loads(result.stdout)
        result_data['status'] = result_data.get('status', 'completed')

        print(f"Rust math task {task_data.get('task_id', 'unknown')} completed")
        return result_data
    except Exception as e:
        task_data['status'] = 'error'
        task_data['error'] = str(e)
        print(f"Error processing Rust math task: {e}")
        return task_data

if __name__ == '__main__':
    # Запуск Celery воркера
    celery_app.start()