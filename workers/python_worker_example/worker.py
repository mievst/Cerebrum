import json
import time
import redis
from moviepy.editor import VideoFileClip
import uuid

class Worker:
    def __init__(self, redis_host='localhost', redis_port=6379, queue_name='task_queue', result_expiry=86400, process_function=None):
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        self.queue_name = queue_name
        self.process_function = process_function
        self.result_expiry = result_expiry  # Время хранения результата в секундах (по умолчанию 1 день)

    def get_task(self):
        """
        Получаем задачу из очереди Redis.
        Задачи добавляются в конец списка queue_name и обрабатываются по принципу FIFO.
        """
        _, task_data = self.redis.blpop(self.queue_name)
        return json.loads(task_data)

    def save_result(self, task_id, result):
        """
        Сохраняем результат в Redis с временным ограничением на хранение.
        """
        self.redis.set(task_id, json.dumps(result))
        self.redis.expire(task_id, self.result_expiry)

    def start(self):
        print(f"Worker started and waiting for tasks in {self.queue_name}. To exit, press CTRL+C.")
        while True:
            try:
                task = self.get_task()
                print(f"Received task: {task}")

                # Обрабатываем задачу через указанную функцию
                if self.process_function:
                    result = self.process_function(task)
                    print(f"Processed task result: {result}")

                    # Сохраняем результат
                    task_id = task.get('task_id', str(uuid.uuid4()))
                    self.save_result(task_id, result)
                    print(f"Result for task_id {task_id} saved to Redis.")

            except Exception as e:
                print(f"Error processing task: {e}")
                time.sleep(1)  # В случае ошибки делаем небольшую паузу

# Пример обработки мат. задач
def process_math_task(task):
    time.sleep(10)
    task['value'] *= 2
    return task

# Запуск воркеров
if __name__ == '__main__':
    math_worker = Worker('math_queue', process_function=process_math_task)
    math_worker.start()
