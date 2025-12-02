import logging
import os
from typing import Optional, Tuple

import requests
from werkzeug.datastructures import FileStorage


class AIAnalyzerClient:
    """Small helper that forwards images to the remote VLM service."""

    def __init__(self, endpoint: Optional[str] = None, timeout: Optional[int] = None) -> None:
        self.endpoint = (endpoint or os.environ.get('VLM_API_URL', 'http://localhost:8001/analyze')).rstrip('/')
        env_timeout = os.environ.get('VLM_TIMEOUT')
        self.timeout = timeout or (int(env_timeout) if env_timeout else 300)
        self._logger = logging.getLogger(__name__)

    def analyze(self, image: FileStorage) -> Tuple[Optional[dict], Optional[str]]:
        if not image:
            return None, 'Файл с изображением не найден'

        filename = image.filename or 'upload.jpg'
        image.stream.seek(0)
        files = {
            'image': (filename, image.stream, image.mimetype or 'application/octet-stream')
        }

        try:
            response = requests.post(
                self.endpoint,
                files=files,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            self._logger.error('Cannot reach VLM service: %s', exc)
            return None, 'Сервис распознавания недоступен'
        except ValueError:
            self._logger.error('VLM service returned non-JSON response')
            return None, 'Сервис распознавания вернул некорректный ответ'

        if not payload.get('success'):
            return None, payload.get('message') or payload.get('error') or 'Не удалось распознать одежду'

        return payload.get('data'), None
