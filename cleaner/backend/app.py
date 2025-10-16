import os
from flask import Flask, request, jsonify
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Force CPU mode (Render has no GPU)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

separator = Separator('spleeter:2stems')

@app.route('/')
def home():
    return '''
    <h2>Welcome to the Audio Separation API!</h2>
    <p>Upload an audio file to separate vocals and accompaniment.</p>
    <form action="/separate" method="post" enctype="multipart/form-data">
        <input type="file" name="audio_file" required>
        <button type="submit">Upload & Separate</button>
    </form>
    '''

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    audio_file = request.files['audio_file']
    filename = secure_filename(audio_file.filename)
    input_path = os.path.join('/tmp', filename)
    output_dir = os.path.join('/tmp', 'output')

    # Ensure directories exist
    os.makedirs(output_dir, exist_ok=True)

    # Save file temporarily
    audio_file.save(input_path)

    try:
        separator.separate_to_file(input_path, output_dir)
        return jsonify({'message': 'Separation complete', 'output_dir': output_dir})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
