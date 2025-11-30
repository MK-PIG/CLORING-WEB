# CLORING-WEB

Веб-приложение для обмена и донации одежды с автоматическим анализом изображений.

## Возможности

- Регистрация и аутентификация пользователей
- Каталог одежды с фильтрацией
- Формы для добавления вещей на обмен и донацию
- Автоматический анализ фотографий одежды с помощью AI-модели BLIP

## AI-анализ изображений

Интегрирована vision-language модель **BLIP** (Salesforce/blip-image-captioning-base), которая автоматически определяет:
- Категорию одежды (футболка, рубашка, джинсы, платье и т.д.)
- Цвет
- Материал
- Состояние (новое, хорошее, удовлетворительное)
- Генерирует описание на русском языке

**Важно:** При первом запуске модель загружается (~900 МБ), что может занять несколько минут. Качество перевода описаний на русский язык может варьироваться, так как используется словарный метод перевода.

## Запуск в Docker

### Быстрый старт (с любого компьютера)

```bash
docker pull galanovaxxx/cloring-web:latest
docker run -d -p 5000:5000 --name cloring-web galanovaxxx/cloring-web:latest
```

Приложение будет доступно по адресу: http://localhost:5000

### Запуск с сохранением данных

```bash
docker run -d -p 5000:5000 \
  -v cloring-data:/app/data \
  -v cloring-static:/app/static \
  --name cloring-web \
  galanovaxxx/cloring-web:latest
```

### Запуск через docker-compose (для разработки)

```bash
docker-compose up -d
```

## Структура проекта

```
.
├── src/                    # Исходный код приложения
│   ├── run.py             # Основной Flask-сервер
│   ├── vlm_analyzer.py    # AI-модель для анализа изображений
│   ├── db.py              # Работа с базой данных
│   ├── validation.py      # Валидация данных
│   └── ...
├── templates/             # HTML-шаблоны
├── tests/                 # Тесты
├── requirements.txt       # Зависимости Python
├── Dockerfile            # Образ Docker
└── docker-compose.yml    # Конфигурация Docker Compose
```

## Технологии

- **Backend:** Flask 3.1.2
- **AI/ML:** PyTorch 2.0+, Transformers 4.40+, BLIP (Salesforce)
- **Database:** SQLite
- **Containerization:** Docker

## Разработка

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск локально

```bash
cd src
python run.py
```

### Запуск тестов

```bash
pytest tests/
```

## Конфигурация AI-модели

Модель BLIP загружается автоматически при первом анализе изображения. Для ручной настройки см. `src/vlm_analyzer.py`.

## Авторы

- MK-PIG - Основной проект
- galanovaxxx - Docker, BLIP интеграция

## Лицензия

Проект для образовательных целей.

