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
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        raise Exception(f"Failed to get video info: {str(e)}")

@app.route('/get-formats', methods=['POST'])
def get_formats():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
        
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        info = get_video_info(url)
        
        formats = []
        # Get combined formats (video + audio)
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                quality = f.get('format_note') or f.get('height') or f.get('quality')
                if quality:
                    formats.append({
                        'itag': f.get('format_id'),
                        'quality': f"{quality}p" if isinstance(quality, int) else str(quality),
                        'ext': f.get('ext', 'mp4'),
                        'type': 'combined'
                    })
        
        # Get video-only formats for higher quality options
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                quality = f.get('format_note') or f.get('height') or f.get('quality')
                if quality and isinstance(quality, int) and quality > 360:
                    formats.append({
                        'itag': f.get('format_id'),
                        'quality': f"{quality}p (video only)",
                        'ext': f.get('ext', 'mp4'),
                        'type': 'video'
                    })
        
        # Sort by quality (convert to int for proper sorting)
        def quality_to_int(q):
            try:
                if isinstance(q, str):
                    return int(q.split('p')[0]) if 'p' in q else 0
                return int(q)
            except:
                return 0
        
        formats.sort(key=lambda x: quality_to_int(x['quality']), reverse=True)
        
        # Remove duplicates while keeping highest quality
        unique_formats = []
        seen_qualities = set()
        for f in formats:
            quality_num = f['quality'].split('p')[0]
            if quality_num not in seen_qualities:
                seen_qualities.add(quality_num)
                unique_formats.append(f)
        
        return jsonify(unique_formats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
        
    url = request.json.get('url')
    itag = request.json.get('itag', 'best')
    quality = request.json.get('quality', '')
    is_video_only = 'video only' in quality if quality else False
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Create a temp directory to store the video
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'quiet': True,
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'format': itag if itag != 'best' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        # For video-only formats, we need to merge with best audio
        if is_video_only:
            ydl_opts['format'] = f'{itag}+bestaudio'
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegMetadata'
            })

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
                return jsonify({'error': 'File not found after download'}), 500

            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{info.get('title', 'video')}.mp4"
            )

        except Exception as e:
            return jsonify({'error': f"Download failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
