FROM python:3.11-slim

WORKDIR /app

# Устанавливаем только необходимые системные пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

# Создаем директории для данных
RUN mkdir -p /app/data /app/static/uploads && \
    useradd -m -u 1000 webuser && \
    chown -R webuser:webuser /app

# Переменные окружения
ENV DATABASE_PATH=/app/data/database.db \
    UPLOAD_FOLDER=/app/static/uploads \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

USER webuser

EXPOSE 5000

CMD ["python", "src/run.py"]