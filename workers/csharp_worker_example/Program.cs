using System.Xml.XPath;
using Newtonsoft.Json.Linq;

namespace CsharpWorkerExample
{
    internal class Program
    {
        public static object processStringTask(object task)
        {
            JObject? data = task as JObject;
            var value = data["text"].ToString();
            data["text"] = value.ToUpper();
            return data;
        }

        static void Main(string[] args)
        {
            Console.WriteLine("Hello, World!");

            using (var worker = new Worker("string_queue", processFunction: processStringTask))
            {
                worker.Start();
            }
        }
    }
}
