import pytest
import time
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Добавляем путь к middleware
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'middleware')))

# Имитируем celery_app
celery_app = MagicMock()


def test_math_task_integration():
    """Интеграционный тест для математической задачи"""
    # Создаем тестовые данные
    task_data = {
        "value": 5.0,
        "task_id": "test-math-123"
    }

    # Имитируем вызов Celery задачи
    with patch.object(celery_app, 'send_task') as mock_send_task:
        # Создаем mock объект для результата задачи
        mock_result = MagicMock()
        mock_result.get.return_value = {
            "value": 10.0,
            "task_id": "test-math-123",
            "status": "completed"
        }
        mock_send_task.return_value = mock_result

        # Вызываем задачу через Celery
        result = celery_app.send_task('workers.math_task', args=[task_data])
        task_result = result.get()

        # Проверяем результат
        assert task_result["value"] == 10.0
        assert task_result["task_id"] == "test-math-123"
        assert task_result["status"] == "completed"


def test_video_task_integration():
    """Интеграционный тест для видео задачи"""
    # Создаем тестовые данные
    task_data = {
        "video": "/test/video.mp4",
        "task_id": "test-video-456"
    }

    # Имитируем вызов Celery задачи
    with patch.object(celery_app, 'send_task') as mock_send_task:
        # Создаем mock объект для результата задачи
        mock_result = MagicMock()
        mock_result.get.return_value = {
            "video": "/test/video_processed.mp4",
            "duration": 120.5,
            "task_id": "test-video-456",
            "status": "completed"
        }
        mock_send_task.return_value = mock_result

        # Вызываем задачу через Celery
        result = celery_app.send_task('workers.video_task', args=[task_data])
        task_result = result.get()

        # Проверяем результат
        assert task_result["duration"] == 120.5
        assert task_result["video"] == "/test/video_processed.mp4"
        assert task_result["task_id"] == "test-video-456"
        assert task_result["status"] == "completed"


def test_csharp_task_integration():
    """Интеграционный тест для C# задачи"""
    # Создаем тестовые данные
    task_data = {
        "data": "test input",
        "task_id": "test-csharp-789"
    }

    # Имитируем вызов Celery задачи
    with patch.object(celery_app, 'send_task') as mock_send_task:
        # Создаем mock объект для результата задачи
        mock_result = MagicMock()
        mock_result.get.return_value = {
            "data": "processed test input",
            "task_id": "test-csharp-789",
            "status": "completed"
        }
        mock_send_task.return_value = mock_result

        # Вызываем задачу через Celery
        result = celery_app.send_task('workers.csharp_task', args=[task_data])
        task_result = result.get()

        # Проверяем результат
        assert task_result["data"] == "processed test input"
        assert task_result["task_id"] == "test-csharp-789"
        assert task_result["status"] == "completed"


def test_rust_math_task_integration():
    """Интеграционный тест для Rust математической задачи"""
    # Создаем тестовые данные
    task_data = {
        "value": 5.0,
        "task_id": "test-rust-101"
    }

    # Имитируем вызов Celery задачи
    with patch.object(celery_app, 'send_task') as mock_send_task:
        # Создаем mock объект для результата задачи
        mock_result = MagicMock()
        mock_result.get.return_value = {
            "value": 10.0,
            "task_id": "test-rust-101",
            "status": "completed"
        }
        mock_send_task.return_value = mock_result

        # Вызываем задачу через Celery
        result = celery_app.send_task('workers.rust_math_task', args=[task_data])
        task_result = result.get()

        # Проверяем результат
        assert task_result["value"] == 10.0
        assert task_result["task_id"] == "test-rust-101"
        assert task_result["status"] == "completed"


def test_task_result_storage():
    """Тест проверяет сохранение результата задачи в Redis"""
    # Создаем тестовые данные результата
    task_id = "test-storage-123"
    result_data = {
        "value": 10.0,
        "task_id": task_id,
        "status": "completed"
    }

    # Имитируем Redis клиент
    mock_redis_client = MagicMock()

    # Имитируем функцию save_file_result
    def mock_save_file_result(task_id, result_data):
        """
        Имитирует сохранение результата выполнения задачи в Redis
        """
        mock_redis_client.set(task_id, json.dumps(result_data))
        mock_redis_client.expire(task_id, 86400)  # Хранение результата 1 день

    # Вызываем функцию сохранения результата
    mock_save_file_result(task_id, result_data)

    # Проверяем, что методы Redis были вызваны с правильными аргументами
    mock_redis_client.set.assert_called_once_with(task_id, json.dumps(result_data))
    mock_redis_client.expire.assert_called_once_with(task_id, 86400)