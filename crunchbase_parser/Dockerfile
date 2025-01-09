# Используем Python как базовый образ
FROM python:3.12-slim

# Устанавливаем зависимости для Chrome
RUN apt-get update && apt-get install -y \
    wget unzip curl \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxrandr2 libxss1 libasound2 libxdamage1 libgbm1 \
    libgtk-3-0 libxcomposite1 libxi6 libxcursor1 libxinerama1 \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
COPY requirements.txt /temp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /temp/requirements.txt

# Копируем приложение
WORKDIR /crunchbase_parser
COPY . /crunchbase_parser

# Устанавливаем порт для FastAPI
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
