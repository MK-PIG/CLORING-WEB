команды для запуска конетйнера:
- docker build -t cloring-web .
- docker run -d --name flask-web -p 8080:5000 -v cloring-data:/app/data -v cloring-uploads:/app/static/uploads cloring-web