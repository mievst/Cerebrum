import pika
import json
import time

class Worker:
    def __init__(self, queue_name, host='rabbitmq', process_function=None):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        self.process_function = process_function

        # Создаем очередь, которую будет слушать воркер
        self.channel.queue_declare(queue=queue_name, durable=True)

    def callback(self, ch, method, properties, body):
        task = json.loads(body)
        print(f"Received task: {task}")

        # Обрабатываем задачу через функцию
        if self.process_function:
            result = self.process_function(task)
            print(f"Processed task result: {result}")

        self.channel.basic_publish(
            exchange='',
            routing_key='results',
            body=json.dumps(result),
            properties=pika.BasicProperties(
                message_id=task['task_id'],
                content_type='application/json',
                delivery_mode=2  # Make the message persistent
            )
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        print(f"Waiting for tasks in {self.queue_name}. To exit press CTRL+C")
        self.channel.start_consuming()

    def close(self):
        self.connection.close()

# Пример обработки мат. задач
def process_math_task(task):
    time.sleep(10)
    task['value'] *= 2
    return task

# Запуск воркеров
if __name__ == '__main__':
    math_worker = Worker('math_queue', process_function=process_math_task)
    math_worker.start()
