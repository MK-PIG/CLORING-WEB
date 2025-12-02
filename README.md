
# CLORING-WEB

Веб-приложение для обмена и доната одежды с AI-анализом фотографий (BLIP), который заполняет карточки вещи полностью на русском языке.

## Быстрый запуск (оба сервиса)

```bash
docker compose up -d
```

- `http://localhost:5000` — пользовательский интерфейс
- `http://localhost:8001/health` — сервис нейросети BLIP

**Важно:** первая обработка фото скачает модель (~900 МБ) для VLM-сервиса. Далее она кэшируется в контейнере.

## Возможности
- Регистрация и каталог вещей пользователей
- Автоанализ фото одежды на русском (тип, цвет, материал, состояние, описание)
- Расширенный словарь и склонения прилагательных под род/число предмета
- Уведомления на фронтенде при ошибках анализа

## Отдельные образы для веба и ИИ

Проект делится на два Docker-образа, которые можно разворачивать на разных виртуальных машинах:

```bash
# VLM сервис (порт 8001)
docker build -f Dockerfile.vlm -t your-registry/cloring-vlm:latest .

# Веб-приложение (порт 5000)
docker build -f Dockerfile.web -t your-registry/cloring-web:latest .
```

### Развертывание на разных ВМ
1. **VLM/нейросеть.**
   ```bash
   docker run -d --name cloring-vlm -p 8001:8001 your-registry/cloring-vlm:latest
   ```
2. **Веб-приложение.** Передайте URL VLM-сервиса через `VLM_API_URL`.
   ```bash
   docker run -d --name cloring-web \
     -e VLM_API_URL="http://<private-ip-or-domain>:8001/analyze" \
     -p 5000:5000 your-registry/cloring-web:latest
   ```
3. Ограничьте доступ к порту 8001 (VPN/Firewall), чтобы VLM был доступен только приложению.

### Готовые образы на Docker Hub `galanovaxxx`

```powershell
docker pull galanovaxxx/cloring-vlm:latest
docker run -d --name cloring-vlm -p 8001:8001 galanovaxxx/cloring-vlm:latest

docker pull galanovaxxx/cloring-web:latest
docker run -d --name cloring-web `
   -e VLM_API_URL="http://<ip-vlm>:8001/analyze" `
   -p 5000:5000 galanovaxxx/cloring-web:latest
```

Для локальной разработки по-прежнему достаточно `docker compose up -d` — оба контейнера общаются по внутренней сети docker.

## Технологии
Flask, Requests, PyTorch, BLIP (Salesforce), Docker

