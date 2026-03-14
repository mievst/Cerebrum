# См. статью по ссылке https://aka.ms/customizecontainer, чтобы узнать как настроить контейнер отладки и как Visual Studio использует этот Dockerfile для создания образов для ускорения отладки.

# Этот этап используется при запуске из VS в быстром режиме (по умолчанию для конфигурации отладки)
FROM mcr.microsoft.com/dotnet/runtime:8.0 AS base
USER app
WORKDIR /app

# Этот этап используется для сборки проекта службы
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["CsharpWorkerExample.csproj", "."]
RUN dotnet restore "./CsharpWorkerExample.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "./CsharpWorkerExample.csproj" -c $BUILD_CONFIGURATION -o /app/build

# Этот этап используется для публикации проекта службы, который будет скопирован на последний этап
FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./CsharpWorkerExample.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

# Этот этап используется в рабочей среде или при запуске из VS в обычном режиме (по умолчанию, когда конфигурация отладки не используется)
FROM base AS final
WORKDIR /app

# Установка Python для поддержки Celery моста
USER root
RUN apt-get update && apt-get install -y python3 python3-pip && apt-get clean
USER app

# Установка Python зависимостей
COPY requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY --from=publish /app/publish .

# Копируем Python мост
COPY celery_bridge.py ./

CMD ["python3", "-m", "celery", "-A", "celery_bridge", "worker", "--loglevel=info"]