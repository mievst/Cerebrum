using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading;
using Newtonsoft.Json;

/*
	Usage:
	var client = new Client("http://localhost:5000");
	var taskId = client.SubmitTask(new { foo = "bar", baz = 42 }, "queue_name");
	var result = client.GetResult(taskId);
	client.UploadFile("path/to/file.txt");
*/

public class Client
{
    private readonly string _serviceUrl;

    public Client(string serviceUrl)
    {
        _serviceUrl = serviceUrl;
    }

    public string SubmitTask(dynamic data, string queueName)
    {
        while (true)
        {
            try
            {
                var content = new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json");
                content.Headers.ContentType = new MediaTypeHeaderValue("application/json");
                var response = new HttpClient().PostAsync($"{_serviceUrl}/submit_task", content).Result;
                response.EnsureSuccessStatusCode();
                var taskId = JsonConvert.DeserializeObject<dynamic>(response.Content.ReadAsStringAsync().Result).task_id;
                Console.WriteLine($"Task submitted with ID: {taskId}");
                return taskId;
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"Error submitting task: {ex.Message}");
                Thread.Sleep(1000); // wait 1 second before retrying
            }
        }
    }

    public string GetResult(string taskId, isWait = true)
    {
        if (isWait)
        {
            while (true)
            {
                var response = new HttpClient().GetAsync($"{_serviceUrl}/get_result/{taskId}").Result;
                if (response.IsSuccessStatusCode)
                {
                    var result = JsonConvert.DeserializeObject<dynamic>(response.Content.ReadAsStringAsync().Result).result;
                    Console.WriteLine($"Result for task {taskId}: {result}");
                    return result;
                }
                else
                {
                    Console.WriteLine($"Task {taskId} result not found or not ready yet");
                    Thread.Sleep(1000); // wait 1 second before retrying
                }
            }
        }
        else {
            var response = new HttpClient().GetAsync($"{_serviceUrl}/get_result/{taskId}").Result;
            if (response.IsSuccessStatusCode)
            {
                var result = JsonConvert.DeserializeObject<dynamic>(response.Content.ReadAsStringAsync().Result).result;
                Console.WriteLine($"Result for task {taskId}: {result}");
                return result;
            }
            else
            {
                Console.WriteLine($"Task {taskId} result not found or not ready yet");
                return null;
            }
        }
    }

    public void UploadFile(string filePath)
    {
        using (var fileStream = new FileStream(filePath, FileMode.Open))
        {
            var fileContent = new StreamContent(fileStream);
            var response = new HttpClient().PostAsync($"{_serviceUrl}/upload_file", fileContent).Result;
            response.EnsureSuccessStatusCode();
        }
    }
}