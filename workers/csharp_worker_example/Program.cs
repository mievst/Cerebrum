using System.Xml.XPath;
using Newtonsoft.Json.Linq;
using System;
using System.Threading.Tasks;

namespace CsharpWorkerExample
{
    internal class Program
    {
        public static JObject processStringTask(JObject task)
        {
            var value = task["text"].ToString();
            task["text"] = value.ToUpper();
            return task;
        }

        public static void Main(string[] args)
        {
            // Проверяем, что переданы аргументы
            if (args.Length == 0)
            {
                Console.WriteLine("No task data provided");
                return;
            }

            try
            {
                // Парсим JSON задачу из аргументов
                string taskJson = args[0];
                JObject task = JObject.Parse(taskJson);

                // Обрабатываем задачу
                JObject result = processStringTask(task);

                // Выводим результат в stdout в формате JSON
                Console.WriteLine(result.ToString());
            }
            catch (Exception ex)
            {
                // В случае ошибки выводим JSON с информацией об ошибке
                JObject errorResult = new JObject
                {
                    ["status"] = "error",
                    ["error"] = ex.Message
                };
                Console.WriteLine(errorResult.ToString());
            }
        }
    }
}
