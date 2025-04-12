import os
from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    # Extract the URL from the request JSON
    url = request.json.get('url')
    
    # Check if URL was provided
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # yt-dlp options
    ydl_opts = {'quiet': True, 'skip_download': True, 'socket_timeout': 10}  # Set a timeout for the request

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info without downloading
            info = ydl.extract_info(url, download=False)
            
            # Return the title and download URL (or webpage URL as fallback)
            return jsonify({
                'title': info['title'],
                'url': info['url'] if 'url' in info else info['webpage_url']
            })
    except yt_dlp.DownloadError as e:
        # Handle download errors
        return jsonify({'error': f"Download error: {str(e)}"}), 400
    except Exception as e:
        # Handle other errors (e.g., network, URL parsing)
        return jsonify({'error': f"Error: {str(e)}"}), 400

if __name__ == '__main__':
    # Get the port from the environment variable set by Railway or default to 5000
    port = os.getenv("PORT", 5000)
    
    # Run the Flask app, binding it to 0.0.0.0 so it's accessible externally
    app.run(host="0.0.0.0", port=port, debug=True)
