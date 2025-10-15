from flask import Flask, request, jsonify, send_file, render_template
from spleeter.separator import Separator
import os
import tempfile

# Tell Flask to look for templates inside the current folder (backend)
app = Flask(__name__, template_folder='.')

# Initialize Spleeter Separator for 2 stems (vocals and accompaniment)
separator = Separator('spleeter:2stems')

@app.route("/")
def home():
    return render_template("index.html")  # Flask will now look for backend/index.html

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file.filename)
    file.save(input_path)

    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    separator.separate_to_file(input_path, output_dir)

    separated_files = {}
    for root, dirs, files in os.walk(output_dir):
        for f in files:
            separated_files[f] = os.path.join(root, f)

    return jsonify({
        'message': 'Separation complete',
        'files': list(separated_files.keys())
    })

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    for root, dirs, files in os.walk(tempfile.gettempdir()):
        if filename in files:
            return send_file(os.path.join(root, filename), as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
