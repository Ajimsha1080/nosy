from flask import Flask, request, jsonify, send_file
from io import BytesIO
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Dummy audio separation function
# Replace this with your real separation code
def separate_audio(file_bytes, filename):
    # In a real case, generate vocals_data and accompaniment_data
    # Here we just return the same file for demonstration
    vocals_io = BytesIO(file_bytes)
    accompaniment_io = BytesIO(file_bytes)

    vocals_io.seek(0)
    accompaniment_io.seek(0)

    vocals_name = f"vocals_{filename}.wav"
    accompaniment_name = f"accompaniment_{filename}.wav"

    return (vocals_io, vocals_name), (accompaniment_io, accompaniment_name)

@app.route('/')
def home():
    return "Audio Separation API is live!"

@app.route('/separate', methods=['POST'])
def separate():
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_bytes = file.read()

    (vocals_io, vocals_name), (acc_io, acc_name) = separate_audio(file_bytes, filename)

    # Return URLs that frontend can use to fetch in-memory files
    # Flask cannot serve in-memory files directly in JSON, so we create routes dynamically
    # Here we store in-memory objects temporarily
    request.environ['vocals_io'] = vocals_io
    request.environ['acc_io'] = acc_io

    return jsonify({
        "message": "Separation complete ✅",
        "vocals_name": vocals_name,
        "accompaniment_name": acc_name
    })

@app.route('/download/<file_type>/<file_name>')
def download(file_type, file_name):
    # Get the file from request context if available
    if file_type == 'vocals':
        file_io = request.environ.get('vocals_io')
    elif file_type == 'accompaniment':
        file_io = request.environ.get('acc_io')
    else:
        return "File not found", 404

    if not file_io:
        return "File expired or not found", 404

    file_io.seek(0)
    return send_file(file_io, download_name=file_name, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
