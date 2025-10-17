from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems')

@app.route('/')
def home():
    return "🎵 Audio Separation API is Live!"

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_dir = os.path.join(OUTPUT_FOLDER, filename.split('.')[0])
    os.makedirs(output_dir, exist_ok=True)

    try:
        separator.separate_to_file(input_path, OUTPUT_FOLDER)
        vocal_path = f"{output_dir}/vocals.wav"
        music_path = f"{output_dir}/accompaniment.wav"

        return jsonify({
            "vocal": f"/download/{filename.split('.')[0]}/vocals.wav",
            "music": f"/download/{filename.split('.')[0]}/accompaniment.wav"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    full_path = os.path.join(OUTPUT_FOLDER, filename)
    directory = os.path.dirname(full_path)
    file = os.path.basename(full_path)
    return send_from_directory(directory, file)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
