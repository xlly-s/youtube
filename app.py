from flask import Flask, request, Response, jsonify
import yt_dlp
from flask_cors import CORS
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, '%(id)s.%(ext)s')

        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo[height<=1080]+bestaudio/best',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info).replace('%(id)s', info['id']).replace('%(ext)s', 'mp4')

            def generate():
                with open(filename, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk

            file_size = os.path.getsize(filename)
            return Response(generate(), mimetype='video/mp4', headers={
                'Content-Disposition': f'attachment; filename="{info["title"]}.mp4"',
                'Content-Length': str(file_size)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
