FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# создание директорий для томов
RUN mkdir -p /app/data /app/static/uploads


# создается пользователь не root а какой то другой юзер для безопасности
RUN useradd -m -u 1000 webuser
RUN chown -R webuser:webuser /app


# переменная окружения для пути в бд
ENV LOG_DIR=/app/data
ENV DATABASE_PATH=/app/data/database.db
ENV UPLOAD_FOLDER=/app/static/uploads
ENV PYTHONPATH=/app

VOLUME /app/data
VOLUME /app/static/uploads

USER webuser

EXPOSE 5000

CMD ["python","src/run.py"]