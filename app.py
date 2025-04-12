from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    
    # Define yt-dlp options to select 1080p video and best audio
    ydl_opts = {
        'quiet': True,
        'skip_download': True,  # Don't download the file, just extract info
        'format': 'bestvideo[height<=?1080]+bestaudio/best',  # Best video up to 1080p and best audio
        'noplaylist': True,  # Avoid playlists if the URL is a playlist
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract video info without downloading
        info = ydl.extract_info(url, download=False)
        
        # Get the direct download URL for the best 1080p video
        download_url = None
        if 'formats' in info:
            for format in info['formats']:
                if format.get('height') == 1080:
                    download_url = format['url']
                    break
            # If no 1080p format, fall back to the best available
            if not download_url:
                download_url = info['formats'][-1]['url']  # The best format available

        if not download_url:
            return jsonify({'error': 'No 1080p format found or no available download link.'}), 400
        
        # Return the video title and the direct download URL
        return jsonify({
            'title': info['title'],
            'url': download_url
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
