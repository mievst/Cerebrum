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

    def upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.service_url}/upload_file", files=files)
            if response.status_code == 201:
                return response.json()['file_url']
            else:
                raise Exception('File upload failed')

    def get_file(self, file_url, file_path):
        try:
            response = requests.get(f"{self.service_url}/get_file", params={'file_url': file_url})
            response.raise_for_status()  # вызвать исключение, если статус-код не 200
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Ошибка скачивания файла: {e}")
            raise Exception('File download failed')

# Использование:
if __name__ == '__main__':
    client = Client('http://localhost:5000')

    while True:
        file_url = client.upload_file('./Shia.mp4')
        print("file_url:", file_url)
        # Отправка задачи
        task_id = client.submit_task({'video': file_url}, "video_queue")

        # Запрос результата по task_id
        time.sleep(60)
        result = client.get_result(task_id)
        print(result)
        client.get_file(result["video"], './Shia_result.mp4')

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
