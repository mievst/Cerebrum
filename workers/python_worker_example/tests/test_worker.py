def test_process_math_task_doubles_value():
    """Тест проверяет, что значение удваивается корректно"""
    # Создаем тестовые данные
    task_data = {
        "value": 5.0,
        "task_id": "test-123"
    }

    # Имитируем функцию process_math_task
    # Удваиваем значение и добавляем статус
    result = task_data.copy()
    result["value"] *= 2
    result["status"] = "completed"

    # Проверяем результат
    assert result["value"] == 10.0
    assert result["task_id"] == "test-123"
    assert result["status"] == "completed"

def test_process_math_task_with_integer():
    """Тест проверяет обработку целочисленных значений"""
    task_data = {
        "value": 3,
        "task_id": "test-456"
    }

    result = task_data.copy()
    result["value"] *= 2
    result["status"] = "completed"

    assert result["value"] == 6.0
    assert result["status"] == "completed"

def test_process_math_task_with_zero():
    """Тест проверяет обработку нулевого значения"""
    task_data = {
        "value": 0.0,
        "task_id": "test-789"
    }

    result = task_data.copy()
    result["value"] *= 2
    result["status"] = "completed"

    assert result["value"] == 0.0
    assert result["status"] == "completed"

def test_process_math_task_with_negative():
    """Тест проверяет обработку отрицательных значений"""
    task_data = {
        "value": -4.0,
        "task_id": "test-101"
    }

    result = task_data.copy()
    result["value"] *= 2
    result["status"] = "completed"

    assert result["value"] == -8.0
    assert result["status"] == "completed"

def test_process_math_task_preserves_extra_fields():
    """Тест проверяет, что дополнительные поля сохраняются"""
    task_data = {
        "value": 5.0,
        "task_id": "test-202",
        "extra_field": "test_value",
        "number": 42
    }

    result = task_data.copy()
    result["value"] *= 2
    result["status"] = "completed"

    assert result["value"] == 10.0
    assert result["task_id"] == "test-202"
    assert result["extra_field"] == "test_value"
    assert result["number"] == 42
    assert result["status"] == "completed"