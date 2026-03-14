# Этап сборки Rust приложения
FROM rust:1-bullseye as builder

WORKDIR /app

# Копируем файлы проекта
COPY Cargo.toml ./
COPY src ./src

# Сборка приложения
RUN cargo build --release

# Финальный этап
FROM debian:bookworm-slim

WORKDIR /app

# Установка необходимых зависимостей для Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
COPY requirements.txt ./
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Копируем скомпилированное Rust приложение
COPY --from=builder /app/target/release/rust_worker ./rust_worker

# Копируем Python мост
COPY celery_bridge.py ./

# Копируем README
COPY README.md ./

# Делаем Rust приложение исполняемым
RUN chmod +x ./rust_worker

# Установка правильной команды запуска
CMD ["celery", "-A", "celery_bridge", "worker", "--loglevel=info"]