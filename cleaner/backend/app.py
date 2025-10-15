from flask import Flask, request, jsonify, send_file, render_template
from spleeter.separator import Separator
import os
import tempfile

app = Flask(__name__)

# Initialize Spleeter Separator for 2 stems (vocals and accompaniment)
separator = Separator('spleeter:2stems')

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/separate', methods=['POST'])
def separate_audio():
    """
    Accepts an uploaded audio file and separates it into stems.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save uploaded file to a temporary location
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file.filename)
    file.save(input_path)

    # Output directory
    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Perform separation
    separator.separate_to_file(input_path, output_dir)

    # Locate separated files (vocals and accompaniment)
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
    """
    Allows downloading of separated files.
    """
    for root, dirs, files in os.walk(tempfile.gettempdir()):
        if filename in files:
            return send_file(os.path.join(root, filename), as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


