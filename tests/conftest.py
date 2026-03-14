import sys
import os
import pytest

# Добавляем путь к middleware
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'middleware')))

# Импортируем celery_app из middleware
import celery_app