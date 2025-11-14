FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# создается пользователь не root а какой то другой юзер для безопасности
RUN useradd -m -u 1000 webuser
RUN chown -R webuser:webuser /app /data
USER webuser

EXPOSE 5000

CMD ["python","run.py"]