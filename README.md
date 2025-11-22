# Проект CLORING
CLORING - платформа на которой вы сможете обменивать вещи с другими пользователями, либо жертвовать ненужные вам вещи благотворительным организациям, НКО и другим фондам, чья деятельность направленна на помощь обществу.

## Команды для успешного запуска приложения:
- docker pull chupapy77/cloring-flask-app:latest
- docker run -d --name flask-web -p 8080:5000 -v cloring-data:/app/data -v cloring-uploads:/app/static/uploads -e LOG_DIR=/app/data cloring-web