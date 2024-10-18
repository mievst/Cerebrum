#include <iostream>
#include <string>
#include <curl/curl.h>
#include <json/json.h>

class Client {
public:
    Client(std::string service_url) : service_url_(service_url) {}

    std::string submit_task(Json::Value data, std::string queue_name) {
        data["queue"] = queue_name;
        std::string json_data = data.toStyledString();
        CURL *curl;
        CURLcode res;
        curl_global_init(CURL_GLOBAL_DEFAULT);
        curl = curl_easy_init();
        if(curl) {
            curl_easy_setopt(curl, CURLOPT_URL, (service_url_ + "/submit_task").c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data.c_str());
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_memory);
            std::string readBuffer;
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
            res = curl_easy_perform(curl);
            if(res != CURLE_OK) {
                std::cerr << "cURL error: " << curl_easy_strerror(res) << std::endl;
            }
            curl_easy_cleanup(curl);
        }
        curl_global_cleanup();
        Json::Value response;
        Json::Reader reader;
        reader.parse(readBuffer, response);
        return response["task_id"].asString();
    }

    Json::Value get_result(std::string task_id, bool is_wait = true) {
        Json::Value result;
        if (is_wait) {
            while (true) {
                CURL *curl;
                CURLcode res;
                curl_global_init(CURL_GLOBAL_DEFAULT);
                curl = curl_easy_init();
                if(curl) {
                    curl_easy_setopt(curl, CURLOPT_URL, (service_url_ + "/get_result/" + task_id).c_str());
                    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_memory);
                    std::string readBuffer;
                    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
                    res = curl_easy_perform(curl);
                    if(res != CURLE_OK) {
                        std::cerr << "cURL error: " << curl_easy_strerror(res) << std::endl;
                    }
                    curl_easy_cleanup(curl);
                }
                curl_global_cleanup();
                Json::Reader reader;
                reader.parse(readBuffer, result);
                if (result.isMember("result")) {
                    break;
                }
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }
        } else {
            CURL *curl;
            CURLcode res;
            curl_global_init(CURL_GLOBAL_DEFAULT);
            curl = curl_easy_init();
            if(curl) {
                curl_easy_setopt(curl, CURLOPT_URL, (service_url_ + "/get_result/" + task_id).c_str());
                curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_memory);
                std::string readBuffer;
                curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
                res = curl_easy_perform(curl);
                if(res != CURLE_OK) {
                    std::cerr << "cURL error: " << curl_easy_strerror(res) << std::endl;
                }
                curl_easy_cleanup(curl);
            }
            curl_global_cleanup();
            Json::Reader reader;
            reader.parse(readBuffer, result);
        }
        return result;
    }

private:
    static size_t write_memory(void *contents, size_t size, size_t nmemb, void *userp) {
        ((std::string*)userp)->append((char*)contents, size * nmemb);
        return size * nmemb;
    }

    std::string service_url_;
};

int main() {
    // Создаем экземпляр класса Client
    Client client("http://localhost:5000");

    // Создаем JSON-объект с данными для отправки на сервер
    Json::Value data;
    data["key1"] = "value1";
    data["key2"] = "value2";

    // Отправляем задачу на сервер
    std::string task_id = client.submit_task(data, "my_queue");

    // Получаем результат выполнения задачи
    Json::Value result = client.get_result(task_id);

    // Выводим результат
    std::cout << "Результат: " << result << std::endl;

    return 0;
}