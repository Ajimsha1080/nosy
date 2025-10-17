import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator
import uuid
import logging

app = Flask(__name__, static_folder="../../frontend", static_url_path="/")
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems', multiprocess=False)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    """Serve frontend page"""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/separate", methods=["POST"])
def separate_audio():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        logging.info(f"Saved uploaded file: {filepath}")

        logging.info("Starting separation...")
        separator.separate_to_file(filepath, OUTPUT_FOLDER)
        logging.info("Separation complete")

        base_name = os.path.splitext(os.path.basename(filename))[0]
        vocals_path = f"{base_name}/vocals.wav"
        accomp_path = f"{base_name}/accompaniment.wav"

        return jsonify({
            "message": "Separation complete!",
            "vocals": vocals_path,
            "accompaniment": accomp_path
        })
    except Exception as e:
        logging.exception("Error during separation:")
        return jsonify({"error": str(e)}), 500


@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
