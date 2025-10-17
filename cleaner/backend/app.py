import os
import uuid
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# Folder to store uploaded and separated audio
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Spleeter 2-stems separator (vocals + accompaniment)
separator = Separator('spleeter:2stems')

@app.route("/", methods=["GET"])
def home():
    return "🎵 Audio Separation API is Live!"

@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = secure_filename(file.filename)
        uid = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
        file.save(input_path)
        logging.info(f"Saved uploaded file: {input_path}")

        # Folder for output
        output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
        os.makedirs(output_folder, exist_ok=True)

        # Perform separation
        logging.info("Starting separation...")
        separator.separate_to_file(input_path, output_folder)

        # Separated files
        base_name = filename.rsplit(".", 1)[0]
        vocals_path = os.path.join(output_folder, base_name, "vocals.wav")
        accompaniment_path = os.path.join(output_folder, base_name, "accompaniment.wav")

        if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
            return jsonify({"error": "Separation failed"}), 500

        # Return filenames (relative to uploads)
        return jsonify({
            "message": "✅ Separation complete!",
            "vocals": f"{uid}_output/{base_name}/vocals.wav",
            "accompaniment": f"{uid}_output/{base_name}/accompaniment.wav"
        })

    except Exception as e:
        logging.exception("Error processing file")
        return jsonify({"error": "Could not process file."}), 500

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
