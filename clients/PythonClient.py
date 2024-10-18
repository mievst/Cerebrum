import requests
import time
import logging


class Client:
    def __init__(self, service_url):
        self.service_url = service_url

    def submit_task(self, data, queue_name):
        while True:
            try:
                data["queue"] = queue_name
                response = requests.post(
                    url=f'{self.service_url}/submit_task',
                    json=data,
                    timeout=10
                    )
                response.raise_for_status()
                task_id = response.json().get('task_id')
                print(f"Task submitted with ID: {task_id}")
                logging.info("Task submitted: %s", data)
                logging.info("Response: %s", response.text)
                return task_id
            except requests.exceptions.RequestException as e:
                logging.error("Error submitting task: %s", e)
                print(f"Error submitting task: {e}")

    def get_result(self, task_id, is_wait=True):
        result = None
        if is_wait:
            while result is None:
                response = requests.get(
                    url=f'{self.service_url}/get_result/{task_id}',
                    timeout=10
                    )
                if response.status_code == 200:
                    result = response.json()
                    print(f"Result for task {task_id}: {result}")
                time.sleep(1)
        else:
            response = requests.get(
                url=f'{self.service_url}/get_result/{task_id}',
                timeout=10
                )
            if response.status_code == 200:
                result = response.json()
                print(f"Result for task {task_id}: {result}")
                return result
            else:
                print(f"Task {task_id} result not found or not ready yet")
                return None

    def upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                url=f"{self.service_url}/upload_file",
                files=files,
                timeout=10
                )
            if response.status_code == 201:
                return response.json()['file_url']
            else:
                raise Exception('File upload failed')

    def get_file(self, file_url, file_path):
        try:
            response = requests.get(
                url=f"{self.service_url}/get_file",
                params={'file_url': file_url},
                timeout=10
                )
            response.raise_for_status()  # вызвать исключение, если статус-код не 200
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Ошибка скачивания файла: {e}")
            raise Exception('File download failed')


# Использование:
if __name__ == '__main__':
    client = Client(service_url='http://localhost:5000')

    while True:
        """
        upload_file_url = client.upload_file('./Shia.mp4')
        print("file_url:", upload_file_url)
        # Отправка задачи
        video_task_id = client.submit_task(
            data={'video': upload_file_url},
            queue_name="video_queue"
            )

        # Запрос результата по video_task_id
        time.sleep(60)
        video_result = client.get_result(task_id=video_task_id)
        print(video_result)
        client.get_file(
            file_url=video_result["video"],
            file_path='./Shia_result.mp4'
            )
        """
        # Отправка задачи
        string_task_id = client.submit_task(
            data={'text': "some text"},
            queue_name="string_queue"
            )

        # Запрос результата по string_task_id
        time.sleep(30)
        string_result = client.get_result(task_id=string_task_id)
        print(string_result)

        # Отправка задачи
        math_task_id = client.submit_task(
            data={'value': 5},
            queue_name="math_queue"
            )

        # Запрос результата по math_task_id
        time.sleep(30)
        math_result = client.get_result(task_id=math_task_id)
        print(math_result)
