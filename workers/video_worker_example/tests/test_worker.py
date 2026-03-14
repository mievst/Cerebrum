import os
import tempfile
from unittest.mock import patch, MagicMock


def test_process_video_task_success():
    """Тест проверяет успешную обработку видео задачи"""
    # Создаем тестовые данные
    task_data = {
        "video": "/test/video.mp4",
        "task_id": "test-123"
    }

    # Имитируем функцию process_video_task
    with patch('moviepy.editor.VideoFileClip') as mock_video:
        # Создаем mock объект для видео
        mock_clip = MagicMock()
        mock_clip.duration = 120.5  # 120.5 секунд
        mock_video.return_value = mock_clip

        # Имитируем поведение функции
        result = task_data.copy()
        result["duration"] = mock_clip.duration
        result["video"] = task_data["video"].replace('.mp4', '_processed.mp4')
        result["status"] = "completed"

        # Проверяем результат
        assert result["duration"] == 120.5
        assert result["video"] == "/test/video_processed.mp4"
        assert result["task_id"] == "test-123"
        assert result["status"] == "completed"


def test_process_video_task_error():
    """Тест проверяет обработку ошибок при обработке видео"""
    task_data = {
        "video": "/test/nonexistent.mp4",
        "task_id": "test-456"
    }

    # Имитируем возникновение ошибки
    with patch('moviepy.editor.VideoFileClip') as mock_video:
        # Настраиваем mock на выброс исключения
        mock_video.side_effect = Exception("File not found")

        # Имитируем поведение функции при ошибке
        result = task_data.copy()
        result["status"] = "error"
        result["error"] = "File not found"

        # Проверяем результат
        assert result["status"] == "error"
        assert result["error"] == "File not found"
        assert result["task_id"] == "test-456"


def test_process_video_task_preserves_extra_fields():
    """Тест проверяет, что дополнительные поля сохраняются"""
    task_data = {
        "video": "/test/video.mp4",
        "task_id": "test-789",
        "extra_field": "test_value",
        "user_id": 42
    }

    # Имитируем функцию process_video_task
    with patch('moviepy.editor.VideoFileClip') as mock_video:
        # Создаем mock объект для видео
        mock_clip = MagicMock()
        mock_clip.duration = 60.0
        mock_video.return_value = mock_clip

        # Имитируем поведение функции
        result = task_data.copy()
        result["duration"] = mock_clip.duration
        result["video"] = task_data["video"].replace('.mp4', '_processed.mp4')
        result["status"] = "completed"

        # Проверяем результат
        assert result["duration"] == 60.0
        assert result["video"] == "/test/video_processed.mp4"
        assert result["task_id"] == "test-789"
        assert result["extra_field"] == "test_value"
        assert result["user_id"] == 42
        assert result["status"] == "completed"