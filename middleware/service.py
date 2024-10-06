from flask import Flask, request, jsonify, send_file
import pika
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
    Функция удаляет файлы, которые старше TIME_LIMIT
    """
    current_time = time.time()

    # Проходим по всем файлам в директории
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.isfile(file_path):
            # Время последнего изменения файла
            file_mtime = os.path.getmtime(file_path)

            # Если файл старше заданного времени, удаляем его
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
    def __init__(self, rabbitmq_host='rabbitmq', redis_host='redis', redis_port=6379):
        self.app = Flask(__name__)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=0)
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_connection, self.rabbitmq_channel = self.connect_rabbitmq()

        # Инициализация маршрутов
        self._setup_routes()

        # Настройка очереди для результатов
        self.rabbitmq_channel.basic_qos(prefetch_count=1)
        self.rabbitmq_channel.queue_declare(queue='results', durable=True)
        self.rabbitmq_channel.basic_consume(
            queue='results', on_message_callback=self.save_result_callback)

    def connect_rabbitmq(self):
        try:
            # Создаем соединение и канал
            connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host))
            channel = connection.channel()
            return connection, channel
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            raise

    def close_rabbitmq_connection(self):
        try:
            if self.rabbitmq_channel and self.rabbitmq_channel.is_open:
                self.rabbitmq_channel.close()
            if self.rabbitmq_connection and self.rabbitmq_connection.is_open:
                self.rabbitmq_connection.close()
        except Exception as e:
            print(f"Error closing RabbitMQ connection: {e}")

    def reconnect_rabbitmq(self):
        self.close_rabbitmq_connection()
        retries = 0
        max_retries = 5
        while retries < max_retries:
            try:
                print(f"Attempting to reconnect to RabbitMQ (Attempt {retries+1})")
                connection = pika.BlockingConnection(pika.ConnectionParameters(self.rabbitmq_host))
                channel = connection.channel()
                channel.queue_declare(queue='results', durable=True)
                channel.basic_consume(queue='results', on_message_callback=self.save_result_callback)
                print("Reconnected to RabbitMQ")
                self.rabbitmq_connection = connection
                self.rabbitmq_channel = channel
                return
            except Exception as e:
                print(f"Failed to reconnect to RabbitMQ: {e}")
                retries += 1
                time.sleep(5)
        raise Exception("Max retries exceeded. Could not reconnect to RabbitMQ.")

    def save_result_callback(self, ch, method, properties, body):
        try:
            print("Received message from RabbitMQ")
            result_message = json.loads(body)
            task_id = result_message['task_id']

            # Логируем этапы работы
            print(f"Saving result for task_id: {task_id} to Redis")

            # Сохранение результата в Redis
            self.redis.set(task_id, json.dumps(result_message))
            self.redis.expire(task_id, 86400)  # Хранение результата 1 день

            print(f"Result for task_id {task_id} saved to Redis")

            # Подтверждаем успешную обработку
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Message for task_id {task_id} acknowledged")
        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

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
            # Проверяем, что параметр существует и файл по указанному пути доступен
            if file_url:
                try:
                    # Отправляем файл
                    return send_file(file_url)
                except FileNotFoundError:
                    return f"File not found {file_url} {os.path.exists(file_url)}", 404
            else:
                return "No file_url provided", 400

        @self.app.route('/submit_task', methods=['POST'])
        def submit_task():
            task = request.json
            task_id = str(uuid.uuid4())  # Генерация уникального task_id
            task["task_id"] = task_id
            queue_name = task.get('queue', 'default_queue')

            max_retries = 3
            retries = 0

            while retries < max_retries:
                try:
                    self.rabbitmq_channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=json.dumps(task),
                        properties=pika.BasicProperties(
                            message_id=task_id,
                            delivery_mode=2,
                            content_type='application/json'
                            )
                    )
                    break
                except Exception as e:
                    print(f"RabbitMQ connection lost: {e}")
                    self.reconnect_rabbitmq()  # В случае ошибки переподключаемся
                    retries += 1
                    time.sleep(1)

            if retries == max_retries:
                return jsonify({'error': 'Failed to publish message after retries'}), 500

            return jsonify({'task_id': task_id}), 202

        @self.app.route('/get_result/<task_id>', methods=['GET'])
        def get_result(task_id):
            result = self.redis.get(task_id)
            if result:
                return jsonify({'task_id': task_id, 'result': json.loads(result)}), 200
            else:
                return jsonify({'error': 'Result not ready or task not found'}), 404

    def run_flask_app(self):
        self.app.run(host='0.0.0.0', port=5000)

    def run(self):
        print("Starting Middleware Service...")
        Thread(target=self.run_flask_app).start()
        print("Starting RabbitMQ Consumer...")

        while True:
            try:
                self.rabbitmq_channel.start_consuming()
            except pika.exceptions.StreamLostError as e:
                print(f"RabbitMQ connection lost: {e}")
                time.sleep(5)
                self.reconnect_rabbitmq()  # Переподключение в случае разрыва соединения
            except Exception as e:
                print(f"Error starting RabbitMQ consumer: {e}")
                time.sleep(5)


# Использование:
if __name__ == '__main__':
    cleanup_thread = Thread(target=run_cleanup_scheduler, daemon=True)
    cleanup_thread.start()
    middleware = MiddlewareService()
    middleware.run()
