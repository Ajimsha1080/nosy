from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import os
from spleeter.separator import Separator

app = Flask(__name__, static_folder='../../frontend', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'separated'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems')

@app.route('/')
def home():
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h2>🎵 Audio Separation API is Live!</h2>", 200

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Create output subfolder per file
    output_dir = os.path.join(OUTPUT_FOLDER, os.path.splitext(file.filename)[0])
    os.makedirs(output_dir, exist_ok=True)

    try:
        separator.separate_to_file(input_path, output_dir)

        vocal_path = os.path.join(output_dir, 'accompaniment', 'accompaniment.wav')
        music_path = os.path.join(output_dir, 'vocals', 'vocals.wav')

        if not os.path.exists(vocal_path) or not os.path.exists(music_path):
            return jsonify({'error': 'Separation failed'}), 500

        return jsonify({
            'vocal': f'/download/{os.path.relpath(vocal_path, OUTPUT_FOLDER)}',
            'music': f'/download/{os.path.relpath(music_path, OUTPUT_FOLDER)}'
        }), 200

    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    dir_name = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    return send_from_directory(directory=dir_name, path=file_name, as_attachment=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
