from flask import Flask, request, jsonify, send_file
import yt_dlp
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided.'}), 400

    # yt-dlp options
    ydl_opts = {
        'quiet': True,
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id")
            file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

            if not os.path.exists(file_path):
                return jsonify({'error': 'Download failed or file not found.'}), 500

            return jsonify({
                'title': info.get('title'),
                'file': f'/file/{video_id}.mp4'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/file/<filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
