from flask import Flask, request, jsonify, send_file
import json
import uuid
from threading import Thread
import time
import os
from middleware.celery_app import celery_app, save_file_result


UPLOAD_FOLDER = '/files'
FILE_TIME_LIMIT = 24 * 60 * 60  # 24 часа

def delete_old_files():
    """
    Функция удаляет файлы, которые старше FILE_TIME_LIMIT
    """
    current_time = time.time()

    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)

            if current_time - file_mtime > FILE_TIME_LIMIT:
                print(f"Deleting old file: {file_path}")
                os.remove(file_path)

def run_cleanup_scheduler(interval=3600):
    """
    Запускает процесс очистки старых файлов каждый `interval` секунд (по умолчанию раз в час)
    """
    while True:
        delete_old_files()
        time.sleep(interval)


class MiddlewareService:
    def __init__(self):
        self.app = Flask(__name__)

        # Инициализация маршрутов
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/upload_file', methods=['POST'])
        def upload_file():
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            return jsonify({'file_url': file_path}), 201

        @self.app.route('/get_file', methods=['GET'])
        def get_file():
            file_url = request.args.get('file_url')
            if file_url:
                try:
                    return send_file(file_url)
                except FileNotFoundError:
                    return f"File not found {file_url}", 404
            else:
                return "No file_url provided", 400

        @self.app.route('/submit_task', methods=['POST'])
        def submit_task():
            task_data = request.json
            task_id = str(uuid.uuid4())
            task_data["task_id"] = task_id

            # Определяем тип задачи и отправляем в соответствующую очередь Celery
            task_type = task_data.get('type', 'default')

            try:
                # Отправка задачи в Celery
                if task_type == 'math':
                    result = celery_app.send_task('workers.math_task', args=[task_data], task_id=task_id)
                elif task_type == 'video':
                    result = celery_app.send_task('workers.video_task', args=[task_data], task_id=task_id)
                else:
                    result = celery_app.send_task('workers.default_task', args=[task_data], task_id=task_id)

                print(f"Task {task_id} added to Celery queue")
            except Exception as e:
                print(f"Error adding task to Celery queue: {e}")
                return jsonify({'error': 'Failed to add task to Celery queue'}), 500

            return jsonify({'task_id': task_id}), 202

        @self.app.route('/get_result/<task_id>', methods=['GET'])
        def get_result(task_id):
            # Попытка получить результат из Redis (для файловых задач)
            result = None
            try:
                result = celery_app.AsyncResult(task_id)
                if result.ready():
                    return jsonify({'task_id': task_id, 'result': result.result}), 200
                else:
                    return jsonify({'task_id': task_id, 'status': 'processing'}), 202
            except:
                # Если задача не найдена в Celery, проверяем в Redis
                pass

            # Если результат не найден в Celery, возвращаем ошибку
            return jsonify({'error': 'Result not ready or task not found'}), 404

    def run_flask_app(self):
        self.app.run(host='0.0.0.0', port=5000)

    def run(self):
        print("Starting Middleware Service...")
        Thread(target=self.run_flask_app).start()
        print("Middleware Service started successfully")


if __name__ == '__main__':
    cleanup_thread = Thread(target=run_cleanup_scheduler, daemon=True)
    cleanup_thread.start()
    middleware = MiddlewareService()
    middleware.run()
