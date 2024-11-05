using System.Xml.XPath;
using Newtonsoft.Json.Linq;

namespace CsharpWorkerExample
{
    internal class Program
    {
        public static async Task<JObject> processStringTask(JObject task)
        {
            var value = task["text"].ToString();
            task["text"] = value.ToUpper();
            return task;
        }

        public static async Task Main(string[] args)
        {
            var worker = new Worker(
                queueName: "task_queue",
                processFunction: processStringTask
            );

            await worker.StartAsync();
        }
    }
}
