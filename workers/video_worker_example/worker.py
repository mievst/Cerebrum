import os

from celery import Celery
from moviepy import VideoFileClip

# Конфигурация Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

# Создание Celery приложения
celery_app = Celery(
    "video_worker", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND
)

# Настройка Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


@celery_app.task(name="workers.video_task")
def process_video_task(task_data):
    """
    Обработка видео задач
    """
    print(f"Processing video task: {task_data}")

    try:
        # Загружаем видео
        video_path = task_data["video"]
        video = VideoFileClip(video_path)
        duration = video.duration
        task_data["duration"] = duration

        # Создаем имя нового видео файла и сохраняем его
        new_video_path = video_path.replace(".mp4", "_processed.mp4")
        video.write_videofile(new_video_path)
        task_data["video"] = new_video_path
        task_data["status"] = "completed"

        print(f"Video task {task_data.get('task_id', 'unknown')} completed")
        return task_data
    except Exception as e:
        task_data["status"] = "error"
        task_data["error"] = str(e)
        print(f"Error processing video task: {e}")
        return task_data


if __name__ == "__main__":
    # Запуск Celery воркера
    celery_app.start()
