# Пример использования Rust воркера

## Отправка задачи через API

Для отправки задачи Rust воркеру, используйте endpoint `/submit_task` middleware сервиса:

```bash
curl -X POST http://localhost:5000/submit_task \
  -H "Content-Type: application/json" \
  -d '{
    "type": "rust_math",
    "value": 5.0,
    "operation": "multiply",
    "multiplier": 3.0
  }'
```

## Поддерживаемые операции

### Умножение
```json
{
  "type": "rust_math",
  "value": 5.0,
  "operation": "multiply",
  "multiplier": 3.0
}
```

### Сложение
```json
{
  "type": "rust_math",
  "value": 5.0,
  "operation": "add",
  "addend": 10.0
}
```

### Возведение в степень
```json
{
  "type": "rust_math",
  "value": 5.0,
  "operation": "power",
  "exponent": 3.0
}
```

### Квадратный корень
```json
{
  "type": "rust_math",
  "value": 25.0,
  "operation": "sqrt"
}
```

### Удвоение (по умолчанию)
```json
{
  "type": "rust_math",
  "value": 5.0
}
```

## Получение результата

После отправки задачи вы получите `task_id`. Используйте его для получения результата:

```bash
curl -X GET http://localhost:5000/get_result/{task_id}
```

## Пример ответа

При успешной обработке вы получите ответ в формате:

```json
{
  "task_id": "unique_task_id",
  "result": {
    "task_id": "unique_task_id",
    "value": 15.0,
    "status": "completed"
  }
}
```

При ошибке:

```json
{
  "task_id": "unique_task_id",
  "result": {
    "task_id": "unique_task_id",
    "value": 5.0,
    "status": "error",
    "error": "Error description"
  }
}