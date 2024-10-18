class Client {
	constructor(serviceUrl) {
		this.serviceUrl = serviceUrl;
	}

	async submitTask(data, queueName) {
		try {
			const response = await fetch(`${this.serviceUrl}/submit_task`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ data, queueName })
			});

			if (response.ok) {
				const taskId = await response.json();
				console.log(`Task submitted: ${taskId}`);
				return taskId;
			} else {
				throw new Error(`Error submitting task: ${response.status}`);
			}
		} catch (error) {
			console.error(`Error submitting task: ${error}`);
			throw error;
		}
	}

	async getResult(taskId, isWait = true) {
		let result = null;
		if (isWait) {
			while (result === null) {
				const response = await fetch(`${this.serviceUrl}/get_result/${taskId}`);
				if (response.ok) {
					result = await response.json();
					console.log(`Result for task ${taskId}: ${result}`);
				} else {
					console.log(`Task ${taskId} result not found or not ready yet`);
				}
				await new Promise(resolve => setTimeout(resolve, 1000));
			}
		} else {
			const response = await fetch(`${this.serviceUrl}/get_result/${taskId}`);
			if (response.ok) {
				result = await response.json();
				console.log(`Result for task ${taskId}: ${result}`);
				return result;
			} else {
				console.log(`Task ${taskId} result not found or not ready yet`);
				return null;
			}
		}
	}

	async uploadFile(filePath) {
		try {
			const file = await fetch(filePath);
			const response = await fetch(`${this.serviceUrl}/upload_file`, {
				method: 'POST',
				body: file.blob()
			});

			if (response.ok) {
				const fileUrl = await response.json();
				return fileUrl;
			} else {
				throw new Error(`Error uploading file: ${response.status}`);
			}
		} catch (error) {
			console.error(`Error uploading file: ${error}`);
			throw error;
		}
	}

	async getFile(fileUrl, filePath) {
		try {
			const response = await fetch(`${this.serviceUrl}/get_file`, {
				method: 'GET',
				params: {
					fileUrl
				}
			});

			if (response.ok) {
				const file = await response.blob();
				await new Promise(resolve => {
					const reader = new FileReader();
					reader.onload = () => {
						const fileContent = reader.result;
						const file = new File([fileContent], filePath, {
							type: 'application/octet-stream'
						});
						resolve(file);
					};
					reader.readAsArrayBuffer(file);
				});
				return file;
			} else {
				throw new Error(`Error downloading file: ${response.status}`);
			}
		} catch (error) {
			console.error(`Error downloading file: ${error}`);
			throw error;
		}
	}
}

// Usage:
const client = new Client('https://api.example.com');

client.submitTask({ foo: 'bar' }, 'queue_name')
	.then(taskId => console.log(`Task submitted: ${taskId}`))
	.catch(error => console.error(`Error submitting task: ${error}`));

client.getResult('task_id')
	.then(result => console.log(`Result for task ${taskId}: ${result}`))
	.catch(error => console.error(`Error getting result: ${error}`));

client.uploadFile('path/to/file.txt')
	.then(fileUrl => console.log(`File uploaded: ${fileUrl}`))
	.catch(error => console.error(`Error uploading file: ${error}`));

client.getFile('file_url', 'path/to/download/file.txt')
	.then(file => console.log(`File downloaded: ${file}`))
	.catch(error => console.error(`Error downloading file: ${error}`));