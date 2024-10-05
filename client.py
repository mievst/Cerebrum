import requests
import time
import logging

class Client:
    def __init__(self, service_url):
        self.service_url = service_url

    def submit_task(self, data, queue_name='default_queue'):
        while True:
            try:
                data["queue"] = queue_name
                response = requests.post(f'{self.service_url}/submit_task', json=data)
                response.raise_for_status()
                task_id = response.json().get('task_id')
                print(f"Task submitted with ID: {task_id}")
                logging.info(f"Task submitted: {data}")
                logging.info(f"Response: {response.text}")
                return task_id
            except requests.exceptions.RequestException as e:
                logging.error(f"Error submitting task: {e}")
                print(f"Error submitting task: {e}")

    def get_result(self, task_id):
        response = requests.get(f'{self.service_url}/get_result/{task_id}')
        if response.status_code == 200:
            result = response.json().get('result')
            print(f"Result for task {task_id}: {result}")
            return result
        else:
            print(f"Task {task_id} result not found or not ready yet")
            return None

# Использование:
if __name__ == '__main__':
    client = Client('http://localhost:5000')

    while True:
        # Отправка задачи
        task_id = client.submit_task({'text': "some text"}, "string_queue")

        # Запрос результата по task_id
        time.sleep(30)
        result = client.get_result(task_id)
        print(result)

        # Отправка задачи
        task_id = client.submit_task({'value': 5}, "math_queue")

        # Запрос результата по task_id
        time.sleep(30)
        result = client.get_result(task_id)
        print(result)
