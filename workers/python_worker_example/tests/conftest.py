import sys
import os
import pytest

# Добавляем путь к директории воркера
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем функцию из worker.py
# Мы импортируем напрямую из файла, так как worker.py не является стандартным модулем
import worker

# Получаем функцию process_math_task из модуля
process_math_task = worker.process_math_task