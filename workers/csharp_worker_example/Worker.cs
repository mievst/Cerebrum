using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using RabbitMQ.Client.Exceptions;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public class Worker : IDisposable
{
    private IConnection? _connection;
    private IModel? _channel;
    private readonly string _queueName;
    private readonly string _hostName;
    private readonly Func<object, object>? _processFunction;
    private bool _isRunning;
    private const int RECONNECT_INTERVAL = 5000; // 5 seconds
    private readonly object _lockObject = new object();

    public Worker(string queueName, string host = "rabbitmq", Func<object, object>? processFunction = null)
    {
        _queueName = queueName;
        _hostName = host;
        _processFunction = processFunction;
        _isRunning = false;
    }

    private bool TryConnect()
    {
        try
        {
            if (_connection?.IsOpen ?? false) return true;

            var factory = new ConnectionFactory
            {
                HostName = _hostName,
                AutomaticRecoveryEnabled = true,
                NetworkRecoveryInterval = TimeSpan.FromSeconds(10)
            };

            _connection = factory.CreateConnection();
            _channel = _connection.CreateModel();

            // Declare the queue that the worker will listen to
            _channel.QueueDeclare(
                queue: _queueName,
                durable: true,
                exclusive: false,
                autoDelete: false,
                arguments: null);

            _channel.BasicQos(0, 1, false);

            Console.WriteLine("Successfully connected to RabbitMQ");
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Failed to connect to RabbitMQ: {ex.Message}");
            return false;
        }
    }

    private void HandleMessage(object? sender, BasicDeliverEventArgs ea)
    {
        try
        {
            var body = ea.Body.ToArray();
            var message = Encoding.UTF8.GetString(body);
            var task = JsonConvert.DeserializeObject<JObject>(message);

            Console.WriteLine($"Received task: {message}");

            object? result = null;
            if (_processFunction != null && task != null)
            {
                result = _processFunction(task);
                Console.WriteLine($"Processed task result: {JsonConvert.SerializeObject(result)}");
            }

            var resultMessage = JsonConvert.SerializeObject(result, new JsonSerializerSettings
            {
                NullValueHandling = NullValueHandling.Ignore
            });
            var resultBody = Encoding.UTF8.GetBytes(resultMessage);

            var properties = _channel?.CreateBasicProperties();
            if (properties != null)
            {
                properties.MessageId = task?["task_id"]?.ToString();
                properties.ContentType = "application/json";
                properties.DeliveryMode = 2; // Persistent

                _channel?.BasicPublish(
                    exchange: "",
                    routingKey: "results",
                    basicProperties: properties,
                    body: resultBody);
            }

            _channel?.BasicAck(ea.DeliveryTag, false);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error processing message: {ex.Message}");
            // Reject message and requeue it
            _channel?.BasicNack(ea.DeliveryTag, false, true);
        }
    }

    public void Start()
    {
        _isRunning = true;

        while (_isRunning)
        {
            try
            {
                if (!TryConnect())
                {
                    Console.WriteLine($"Connection failed. Retrying in {RECONNECT_INTERVAL/1000} seconds...");
                    Thread.Sleep(RECONNECT_INTERVAL);
                    continue;
                }

                var consumer = new EventingBasicConsumer(_channel);
                consumer.Received += HandleMessage;
                consumer.Shutdown += (sender, ea) =>
                {
                    Console.WriteLine("Consumer shutdown. Attempting to reconnect...");
                };
                consumer.ConsumerCancelled += (sender, ea) =>
                {
                    Console.WriteLine("Consumer cancelled. Attempting to reconnect...");
                };

                _channel?.BasicConsume(
                    queue: _queueName,
                    autoAck: false,
                    consumer: consumer);

                Console.WriteLine($"Waiting for tasks in {_queueName}. To exit press CTRL+C");

                // Keep checking connection status
                while (_isRunning && (_connection?.IsOpen ?? false))
                {
                    Thread.Sleep(1000);
                }

                if (_isRunning)
                {
                    Console.WriteLine("Connection lost. Attempting to reconnect...");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in consumer loop: {ex.Message}");
                Thread.Sleep(RECONNECT_INTERVAL);
            }
        }
    }

    public void Stop()
    {
        _isRunning = false;
        Dispose();
    }

    public void Dispose()
    {
        try
        {
            _channel?.Close();
            _channel?.Dispose();
            _connection?.Close();
            _connection?.Dispose();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error during disposal: {ex.Message}");
        }
    }
}