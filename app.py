from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/formats', methods=['POST'])
def formats():
    url = request.json.get('url')

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Filter to progressive MP4 (has both audio + video in one file)
            mp4_formats = [
                {
                    'format_id': f['format_id'],
                    'resolution': f.get('height'),
                    'ext': f.get('ext'),
                    'filesize': f.get('filesize'),
                    'url': f.get('url')
                }
                for f in formats
                if f.get('ext') == 'mp4' and f.get('acodec') != 'none' and f.get('vcodec') != 'none'
            ]

            # Sort by resolution descending
            mp4_formats.sort(key=lambda x: x['resolution'] or 0, reverse=True)

            return jsonify({
                'title': info.get('title', 'video'),
                'formats': mp4_formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
