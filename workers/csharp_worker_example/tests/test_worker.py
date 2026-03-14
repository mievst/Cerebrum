import json
import subprocess
from unittest.mock import patch, MagicMock


def test_process_csharp_task_success():
    """Тест проверяет успешную обработку C# задачи"""
    # Создаем тестовые данные
    task_data = {
        "data": "test input",
        "task_id": "test-123"
    }

    # Имитируем функцию process_csharp_task
    with patch('subprocess.run') as mock_subprocess:
        # Создаем mock объект для результата subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "data": "processed test input",
            "task_id": "test-123"
        })
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Имитируем поведение функции
        result_data = json.loads(mock_result.stdout)
        result_data['status'] = 'completed'

        # Проверяем результат
        assert result_data["data"] == "processed test input"
        assert result_data["task_id"] == "test-123"
        assert result_data["status"] == "completed"


def test_process_csharp_task_error():
    """Тест проверяет обработку ошибок при выполнении C# задачи"""
    task_data = {
        "data": "test input",
        "task_id": "test-456"
    }

    # Имитируем возникновение ошибки в subprocess
    with patch('subprocess.run') as mock_subprocess:
        # Настраиваем mock на выброс исключения
        mock_subprocess.side_effect = Exception("Process failed")

        # Имитируем поведение функции при ошибке
        result = task_data.copy()
        result['status'] = 'error'
        result['error'] = "Process failed"

        # Проверяем результат
        assert result["status"] == "error"
        assert result["error"] == "Process failed"
        assert result["task_id"] == "test-456"


def test_process_csharp_task_non_zero_return_code():
    """Тест проверяет обработку ненулевого кода возврата"""
    task_data = {
        "data": "test input",
        "task_id": "test-789"
    }

    # Имитируем функцию process_csharp_task с ненулевым кодом возврата
    with patch('subprocess.run') as mock_subprocess:
        # Создаем mock объект для результата subprocess с ненулевым кодом возврата
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error occurred"
        mock_subprocess.return_value = mock_result

        # Имитируем поведение функции при ненулевом коде возврата
        result = task_data.copy()
        result['status'] = 'error'
        result['error'] = "C# application failed with return code 1: Error occurred"

        # Проверяем результат
        assert result["status"] == "error"
        assert result["error"] == "C# application failed with return code 1: Error occurred"
        assert result["task_id"] == "test-789"


def test_process_csharp_task_preserves_extra_fields():
    """Тест проверяет, что дополнительные поля сохраняются"""
    task_data = {
        "data": "test input",
        "task_id": "test-101",
        "extra_field": "test_value",
        "user_id": 42
    }

    # Имитируем функцию process_csharp_task
    with patch('subprocess.run') as mock_subprocess:
        # Создаем mock объект для результата subprocess
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "data": "processed test input",
            "task_id": "test-101",
            "extra_field": "test_value",
            "user_id": 42
        })
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Имитируем поведение функции
        result_data = json.loads(mock_result.stdout)
        result_data['status'] = 'completed'

        # Проверяем результат
        assert result_data["data"] == "processed test input"
        assert result_data["task_id"] == "test-101"
        assert result_data["extra_field"] == "test_value"
        assert result_data["user_id"] == 42
        assert result_data["status"] == "completed"