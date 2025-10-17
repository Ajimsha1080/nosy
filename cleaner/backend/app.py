import os
import uuid
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from spleeter.separator import Separator

app = Flask(__name__)
CORS(app)  # allow frontend requests

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Spleeter 2-stems separator (vocals + accompaniment)
separator = Separator('spleeter:2stems')

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def home():
    return "🎵 Audio Separation API is Live!"

@app.route("/separate", methods=["POST"])
def separate():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        filename = secure_filename(file.filename)
        uid = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
        file.save(input_path)
        logging.info(f"Saved uploaded file: {input_path}")

        # Output folder
        output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
        os.makedirs(output_folder, exist_ok=True)

        logging.info("Starting separation...")
        separator.separate_to_file(input_path, output_folder)
        logging.info("Separation complete!")

        # Construct relative paths for frontend
        base_name = filename.rsplit(".", 1)[0]
        vocals_path = os.path.join(f"{uid}_output", base_name, "vocals.wav")
        accompaniment_path = os.path.join(f"{uid}_output", base_name, "accompaniment.wav")

        return jsonify({
            "message": "Separation complete ✅",
            "vocals": vocals_path,
            "accompaniment": accompaniment_path
        })

    except Exception as e:
        logging.exception("Separation failed")
        return jsonify({"error": "Could not process file.", "details": str(e)}), 500


@app.route("/download/<path:filepath>", methods=["GET"])
def download_file(filepath):
    full_path = os.path.join(UPLOAD_FOLDER, filepath)
    if os.path.exists(full_path):
        return send_file(full_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
