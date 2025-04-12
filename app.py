from flask import Flask, request, jsonify
import yt_dlp
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    ydl_opts = {'quiet': True, 'skip_download': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            response = {
                'title': info['title'],
                'url': info['url'] if 'url' in info else info['webpage_url']
            }
            print(f"Response: {response}")  # Log response to the console
            return jsonify(response)
    except yt_dlp.DownloadError as e:
        error_response = {'error': f"Download error: {str(e)}"}
        print(f"Error Response: {error_response}")  # Log error response to console
        return jsonify(error_response), 400
    except Exception as e:
        error_response = {'error': f"Error: {str(e)}"}
        print(f"Error Response: {error_response}")  # Log error response to console
        return jsonify(error_response), 400

if __name__ == '__main__':
    port = os.getenv("PORT", 5000)  # Get the port from the environment or default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
