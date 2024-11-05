from flask import Flask, request, jsonify, send_file
import redis
import json
import uuid
from threading import Thread
import time
import os


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
    def __init__(self, redis_host='redis', redis_port=6379):
        self.app = Flask(__name__)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)

        # Инициализация маршрутов
        self._setup_routes()

    def save_result(self, task_id, result_data):
        """
        Сохраняет результат выполнения задачи в Redis
        """
        self.redis.set(task_id, json.dumps(result_data))
        self.redis.expire(task_id, 86400)  # Хранение результата 1 день

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
            task = request.json
            task_id = str(uuid.uuid4())
            task["task_id"] = task_id
            queue_name = task.get('queue', 'default_queue')

            try:
                # Добавление задачи в Redis очередь
                self.redis.lpush(queue_name, json.dumps(task))
                print(f"Task {task_id} added to queue {queue_name}")
            except Exception as e:
                print(f"Error adding task to queue: {e}")
                return jsonify({'error': 'Failed to add task to queue'}), 500

            return jsonify({'task_id': task_id}), 202

        @self.app.route('/get_result/<task_id>', methods=['GET'])
        def get_result(task_id):
            result = self.redis.get(task_id)
            if result:
                return jsonify({'task_id': task_id, 'result': json.loads(result)}), 200
            else:
                return jsonify({'error': 'Result not ready or task not found'}), 404

    def process_tasks(self, queue_name='default_queue'):
        """
        Обработчик задач из Redis очереди
        """
        while True:
            try:
                task_data = self.redis.brpop(queue_name, timeout=0)
                if task_data:
                    _, task = task_data
                    task = json.loads(task)

                    # Обработка задачи
                    task_id = task["task_id"]
                    print(f"Processing task {task_id}")

                    # Пример обработки задачи, результатом будет словарь
                    result_data = {"task_id": task_id, "status": "completed"}

                    # Сохранение результата в Redis
                    self.save_result(task_id, result_data)
                    print(f"Task {task_id} completed and result saved")
            except Exception as e:
                print(f"Error processing task: {e}")
                time.sleep(1)

    def run_flask_app(self):
        self.app.run(host='0.0.0.0', port=5000)

    def run(self):
        print("Starting Middleware Service...")
        Thread(target=self.run_flask_app).start()
        print("Starting Task Processor...")

        # Запуск обработчика задач для разных очередей
        Thread(target=self.process_tasks, args=('default_queue',)).start()


if __name__ == '__main__':
    cleanup_thread = Thread(target=run_cleanup_scheduler, daemon=True)
    cleanup_thread.start()
    middleware = MiddlewareService()
    middleware.run()
