from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/separated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_dir = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0])
    os.makedirs(output_dir, exist_ok=True)

    separator.separate_to_file(input_path, output_dir)

    vocals_path = f"separated/{os.path.splitext(filename)[0]}/vocals.wav"
    instrumental_path = f"separated/{os.path.splitext(filename)[0]}/accompaniment.wav"

    return jsonify({
        'vocals': vocals_path,
        'instrumental': instrumental_path
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
