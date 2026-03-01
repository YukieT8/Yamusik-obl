import os
import re
from flask import Flask, render_template, request, jsonify
from yandex_music import Client

app = Flask(__name__)

# Инициализация клиента
# Для публичных треков авторизация обычно не требуется
client = Client().init()

def extract_track_id(url):
    # Извлекает ID трека из разных типов ссылок Яндекса
    match = re.search(r'track/(\d+)', url)
    return match.group(1) if match else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_cover', methods=['POST'])
def get_cover():
    try:
        data = request.json
        url = data.get('url', '')
        track_id = extract_track_id(url)
        
        if not track_id:
            return jsonify({'success': False, 'error': 'Не удалось найти ID трека в ссылке'}), 400
        
        # Получаем данные о треке через API
        tracks = client.tracks([track_id])
        if not tracks:
            return jsonify({'success': False, 'error': 'Трек не найден'}), 404
            
        track = tracks[0]
        # Заменяем шаблон на максимальное разрешение
        cover_url = track.get_cover_url(size='1000x1000')
        
        return jsonify({
            'success': True, 
            'url': 'https://' + cover_url,
            'title': track.title,
            'artist': track.artists[0].name if track.artists else 'Unknown'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Порт берется из переменной окружения (нужно для Render/Railway)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
