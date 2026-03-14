use serde::{Deserialize, Serialize};
use serde_json::{Value, from_str, to_string};
use std::env;
use std::io::{self, Read};

#[derive(Serialize, Deserialize, Debug)]
struct Task {
    task_id: Option<String>,
    value: f64,
    operation: String,
    #[serde(flatten)]
    extra: std::collections::HashMap<String, Value>,
}

#[derive(Serialize, Deserialize, Debug)]
struct TaskResult {
    task_id: Option<String>,
    value: f64,
    status: String,
    error: Option<String>,
    #[serde(flatten)]
    extra: std::collections::HashMap<String, Value>,
}

fn process_math_task(task: &mut Task) -> Result<TaskResult, String> {
    println!("Processing math task: {:?}", task);

    // Имитация длительной обработки
    // std::thread::sleep(std::time::Duration::from_secs(2));

    // Выполняем математическую операцию
    let result = match task.operation.as_str() {
        "multiply" => {
            let multiplier = task.extra.get("multiplier")
                .and_then(|v| v.as_f64())
                .unwrap_or(2.0);
            task.value * multiplier
        },
        "add" => {
            let addend = task.extra.get("addend")
                .and_then(|v| v.as_f64())
                .unwrap_or(10.0);
            task.value + addend
        },
        "power" => {
            let exponent = task.extra.get("exponent")
                .and_then(|v| v.as_f64())
                .unwrap_or(2.0);
            task.value.powf(exponent)
        },
        "sqrt" => {
            if task.value < 0.0 {
                return Err("Cannot calculate square root of negative number".to_string());
            }
            task.value.sqrt()
        },
        _ => {
            // По умолчанию удваиваем значение
            task.value * 2.0
        }
    };

    task.value = result;

    Ok(TaskResult {
        task_id: task.task_id.clone(),
        value: task.value,
        status: "completed".to_string(),
        error: None,
        extra: task.extra.clone(),
    })
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    // Если нет аргументов, читаем из stdin
    let task_json = if args.len() > 1 {
        args[1].clone()
    } else {
        let mut buffer = String::new();
        io::stdin().read_to_string(&mut buffer)?;
        buffer
    };

    // Парсим JSON задачу
    let mut task: Task = from_str(&task_json)
        .map_err(|e| format!("Failed to parse task JSON: {}", e))?;

    // Обрабатываем задачу
    let result = process_math_task(&mut task);

    // Выводим результат в stdout в формате JSON
    match result {
        Ok(task_result) => {
            let result_json = to_string(&task_result)
                .map_err(|e| format!("Failed to serialize result: {}", e))?;
            println!("{}", result_json);
        },
        Err(error) => {
            let error_result = TaskResult {
                task_id: task.task_id.clone(),
                value: task.value,
                status: "error".to_string(),
                error: Some(error),
                extra: task.extra.clone(),
            };
            let result_json = to_string(&error_result)
                .map_err(|e| format!("Failed to serialize error result: {}", e))?;
            println!("{}", result_json);
        }
    }

    Ok(())
}