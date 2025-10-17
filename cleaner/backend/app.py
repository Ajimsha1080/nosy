import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
SEPARATED_FOLDER = "separated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SEPARATED_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems', multiprocess=False)

@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>")
def serve_files(path):
    return send_from_directory("../frontend", path)

@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    ext = file.filename.rsplit('.', 1)[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(file_path)

    try:
        # Spleeter output path
        output_dir = os.path.join(SEPARATED_FOLDER, str(uuid.uuid4()))
        os.makedirs(output_dir, exist_ok=True)

        separator.separate_to_file(file_path, output_dir)

        # Spleeter creates /vocals.wav and /accompaniment.wav
        vocals_file = os.path.join(output_dir, "vocals.wav")
        acc_file = os.path.join(output_dir, "accompaniment.wav")

        return jsonify({
            "message": "Separation complete!",
            "vocals": os.path.relpath(vocals_file),
            "accompaniment": os.path.relpath(acc_file)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<path:filename>")
def download_file(filename):
    directory = os.path.dirname(filename)
    filename_only = os.path.basename(filename)
    return send_from_directory(directory, filename_only, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
