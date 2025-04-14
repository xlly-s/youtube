from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,  # Do NOT download, just extract info
        'format': 'bestvideo[height<=?1080]+bestaudio/best',
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        # Find best available MP4 URL
        mp4_url = None
        for f in info['formats']:
            if f.get('ext') == 'mp4' and f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                mp4_url = f['url']
                break

        if not mp4_url:
            return jsonify({'error': 'Could not find MP4 download URL'}), 400

        return jsonify({
            'title': info.get('title', 'video'),
            'url': mp4_url
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
