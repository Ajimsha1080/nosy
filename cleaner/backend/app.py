from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from spleeter.separator import Separator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Spleeter model (2 stems: vocals + accompaniment)
separator = Separator("spleeter:2stems")

@app.route("/", methods=["GET"])
def home():
    return "🎵 Audio Separation API is Live!"

@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        separator.separate_to_file(filepath, OUTPUT_FOLDER)

        base_name = os.path.splitext(filename)[0]
        out_dir = os.path.join(OUTPUT_FOLDER, base_name)

        vocals_path = f"/download/{base_name}/vocals.wav"
        accomp_path = f"/download/{base_name}/accompaniment.wav"

        return jsonify({
            "message": "✅ Separation complete!",
            "vocals": vocals_path,
            "accompaniment": accomp_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<folder>/<filename>")
def download(folder, filename):
    return send_from_directory(os.path.join(OUTPUT_FOLDER, folder), filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
