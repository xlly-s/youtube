from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    
    # Define yt-dlp options to prefer MP4 format, explicitly avoid HLS
    ydl_opts = {
        'quiet': True,
        'skip_download': False,  # Actually download the video
        'format': 'bestvideo[height<=?1080]+bestaudio/best',  # Best video up to 1080p and best audio
        'noplaylist': True,  # Avoid playlists if the URL is a playlist
        'prefer_free_formats': True,  # Prefer free formats like MP4 over others
        'outtmpl': '%(id)s.%(ext)s',  # Template for output file names
        'merge_output_format': 'mp4',  # Force the output format to mp4
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract video info and download the video
        info = ydl.extract_info(url, download=True)
        
        # Get the direct download URL for the best available MP4 format
        download_url = None
        for format in info['formats']:
            if format.get('ext') == 'mp4' and format.get('height') == 1080:
                download_url = format['url']
                break
            elif format.get('ext') == 'mp4':
                download_url = format['url']
        
        if not download_url:
            return jsonify({'error': 'No MP4 format found or no available download link.'}), 400
        
        # Return the video title and the direct download URL
        return jsonify({
            'title': info['title'],
            'url': download_url
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
