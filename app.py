from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    
    # Define yt-dlp options
    ydl_opts = {
        'quiet': True,
        'skip_download': True,  # Don't download the file, just extract info
        'format': 'bestvideo[height<=?1080]+bestaudio/best',  # Best video up to 1080p and best audio
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract video info without downloading
        info = ydl.extract_info(url, download=False)
        
        # Return the video title and the best download link for the selected format
        return jsonify({
            'title': info['title'],
            'url': info['url'] if 'url' in info else info['webpage_url']
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
