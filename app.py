from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({
            'title': info['title'],
            'url': info['url'] if 'url' in info else info['webpage_url']
        })
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
