import os
import tempfile

from flask import Flask, jsonify, request

from src.vlm_analyzer import get_analyzer

app = Flask(__name__)
UPLOAD_DIR = os.environ.get('VLM_UPLOAD_DIR', '/tmp/vlm_uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _save_temp_file(file_storage) -> str:
    suffix = os.path.splitext(file_storage.filename or '')[1] or '.jpg'
    fd, temp_path = tempfile.mkstemp(dir=UPLOAD_DIR, suffix=suffix)
    with os.fdopen(fd, 'wb') as tmp:
        file_storage.save(tmp)
    return temp_path


@app.route('/health', methods=['GET'])
def health() -> tuple:
    return jsonify({'status': 'ok'}), 200


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'image field is required'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'empty filename'}), 400

    temp_path = _save_temp_file(file)
    analyzer = get_analyzer()

    try:
        app.logger.info('Analyzing %s', temp_path)
        result = analyzer.analyze_image(temp_path)
        if result:
            return jsonify({'success': True, 'data': result})
        return jsonify({
            'success': False,
            'message': 'Не удалось распознать одежду. Введите данные самостоятельно.'
        }), 200
    except Exception as exc:  # pragma: no cover
        app.logger.exception('VLM analyzer failed')
        return jsonify({'success': False, 'error': str(exc)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port)
