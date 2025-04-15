from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import tempfile
import os

app = Flask(__name__)
CORS(app)

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'force_generic_extractor': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

@app.route('/get-formats', methods=['POST'])
def get_formats():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        info = get_video_info(url)
        
        formats = []
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':  # Only formats with both video and audio
                quality = f.get('format_note') or f.get('height') or f.get('quality')
                if quality:
                    formats.append({
                        'itag': f.get('format_id'),
                        'quality': f"{quality}p" if isinstance(quality, int) else str(quality),
                        'ext': f.get('ext', 'mp4')
                    })
        
        # Remove duplicates and sort by quality
        unique_formats = []
        seen = set()
        for f in sorted(formats, key=lambda x: int(x['quality'].replace('p', '')) if x['quality'].endswith('p') else 0, reverse=True):
            key = f['quality']
            if key not in seen:
                seen.add(key)
                unique_formats.append(f)
        
        return jsonify(unique_formats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    itag = request.json.get('itag', 'best')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Create a temp directory to store the video
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'quiet': True,
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'format': itag if itag != 'best' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Ensure the file has .mp4 extension
                if not filename.endswith('.mp4'):
                    new_filename = os.path.splitext(filename)[0] + '.mp4'
                    os.rename(filename, new_filename)
                    filename = new_filename

            if not os.path.exists(filename):
                return jsonify({'error': 'File not found'}), 500

            # Send the file as an attachment
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{info.get('title', 'video')}.mp4"
            )

        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
