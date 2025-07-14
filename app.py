from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import uuid
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)  # ⬅️ INI WAJIB agar frontend bisa akses

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return jsonify({"message": "TwilightTone API is running."})

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "No URL provided."}), 400

        # Setup YDL options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title')
            duration = info.get('duration')
            thumbnail = info.get('thumbnail')

            filename = f"{title}.mp3"
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)

            if not os.path.exists(file_path):
                return jsonify({"error": "Failed to download file"}), 500

            return jsonify({
                "title": title,
                "duration": duration,
                "thumbnail": thumbnail,
                "file_url": f"https://twilighttone-backend.up.railway.app/file/{filename}"
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/file/<filename>')
def serve_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
