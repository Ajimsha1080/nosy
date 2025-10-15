from flask import Flask, request, jsonify, send_file, render_template
from spleeter.separator import Separator
import os
import tempfile
import zipfile

app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize Spleeter Separator for 2 stems
separator = Separator('spleeter:2stems')

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Create temp directories
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file.filename)
    file.save(input_path)

    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Separate audio
    separator.separate_to_file(input_path, output_dir)

    # Zip the separated files
    zip_path = os.path.join(temp_dir, "separated_audio.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(output_dir):
            for f in files:
                zipf.write(os.path.join(root, f), arcname=f)

    # Send the zip file
    return send_file(zip_path, as_attachment=True, download_name="separated_audio.zip")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
