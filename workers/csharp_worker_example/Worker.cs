using StackExchange.Redis;
using Newtonsoft.Json.Linq;
using System;
using System.Threading.Tasks;

public class Worker
{
    private readonly ConnectionMultiplexer redis;
    private readonly IDatabase db;
    private readonly string queueName;
    private readonly Func<JObject, Task<JObject>> processFunction;
    private readonly TimeSpan resultExpiry;

    public Worker(string queueName, Func<JObject, Task<JObject>> processFunction, string redisHost = "localhost", int redisPort = 6379, int resultExpiryInSeconds = 86400)
    {
        this.redis = ConnectionMultiplexer.Connect($"{redisHost}:{redisPort}");
        this.db = redis.GetDatabase();
        this.queueName = queueName;
        this.processFunction = processFunction;
        this.resultExpiry = TimeSpan.FromSeconds(resultExpiryInSeconds);
    }

    public async Task StartAsync()
    {
        Console.WriteLine($"Worker started and waiting for tasks in {queueName}. To exit, press CTRL+C.");
        while (true)
        {
            try
            {
                // Получение задачи из очереди
                var taskData = await db.ListLeftPopAsync(queueName);
                if (taskData.IsNullOrEmpty)
                {
                    await Task.Delay(500); // если задач нет, подождать
                    continue;
                }

                // Десериализация задачи в JObject
                var task = JObject.Parse(taskData);
                Console.WriteLine($"Received task: {taskData}");

                // Обработка задачи через переданную функцию
                var result = await processFunction(task);
                Console.WriteLine($"Processed task result: {result}");

                // Сохранение результата
                string taskId = task["task_id"]?.ToString() ?? Guid.NewGuid().ToString();
                await SaveResultAsync(taskId, result);
                Console.WriteLine($"Result for task_id {taskId} saved to Redis.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing task: {ex.Message}");
                await Task.Delay(1000); // Пауза перед повтором
            }
        }
    }

    private async Task SaveResultAsync(string taskId, JObject result)
    {
        // Сохранение результата с установкой времени жизни
        string resultJson = result.ToString();
        await db.StringSetAsync(taskId, resultJson, resultExpiry);
    }
}