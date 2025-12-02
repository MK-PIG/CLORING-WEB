FROM python:3.13-slim

WORKDIR /app

# Копирование только requirements.txt для кеширования слоя
COPY requirements.txt .

# установка зависимостей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование файлов приложения
COPY src/ ./src/
COPY templates/ ./templates/

# создание необходимых директорий и добавление новых пользователей
RUN mkdir -p /app/data /app/static/uploads && \
    useradd -m -u 1000 webuser && \
    chown -R webuser:webuser /app


# переменная окружения для пути в бд
ENV DATABASE_PATH=/app/data/database.db \
    UPLOAD_FOLDER=/app/static/uploads \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

VOLUME /app/data
VOLUME /app/static/uploads

USER webuser

EXPOSE 5000

HEALTHCHECK --interval=600s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000'); print('ok')" || exit 1

CMD ["python","src/run.py"]