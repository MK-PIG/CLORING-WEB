# Проект CLORING
CLORING - платформа на которой вы сможете обменивать вещи с другими пользователями, либо жертвовать ненужные вам вещи благотворительным организациям, НКО и другим фондам, чья деятельность направленна на помощь обществу.

## Предварительные требования
- Python 3.11
- pip

## Установка
### Клонирование репозитория:
```
git clone https://github.com/
cd папка
```


## Команды для успешного запуска приложения:
- docker pull chupapy77/cloring-flask-app:latest
- docker run -d --name flask-web -p 8080:5000 -v cloring-data:/app/data -v cloring-uploads:/app/static/uploads -e LOG_DIR=/app/data cloring-web

## Основные функции
1. Обмен одеждой
2. Пожертвование одежды

```
## Структура проекта
project/
├── app.py              # Основной файл приложения
├── requirements.txt    # Зависимости Python
├── tests/              # Тесты
│   └── test_api.py
└── docs/              
    └── api.md
```

