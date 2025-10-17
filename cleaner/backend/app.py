import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator
import uuid

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "separated")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

separator = Separator('spleeter:2stems', multiprocess=False)

# Serve frontend
@app.route("/")
def index():
    return app.send_static_file("index.html")

# Handle audio separation
@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{file.filename}")
    output_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(os.path.basename(input_path))[0])
    os.makedirs(output_path, exist_ok=True)
    file.save(input_path)

    # Run Spleeter
    separator.separate_to_file(input_path, OUTPUT_FOLDER)

    vocals_file = os.path.join(output_path, "vocals.wav")
    accompaniment_file = os.path.join(output_path, "accompaniment.wav")

    return jsonify({
        "message": "Separation complete",
        "vocals": f"/download/{os.path.relpath(vocals_file, BASE_DIR)}",
        "accompaniment": f"/download/{os.path.relpath(accompaniment_file, BASE_DIR)}"
    })

# Serve separated files
@app.route("/download/<path:filepath>")
def download_file(filepath):
    abs_path = os.path.join(BASE_DIR, filepath)
    directory = os.path.dirname(abs_path)
    filename = os.path.basename(abs_path)
    return send_from_directory(directory, filename, as_attachment=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
