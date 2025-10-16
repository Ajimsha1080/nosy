import os
import uuid
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize separator
separator = Separator("spleeter:2stems")

logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    # Serve frontend
    return app.send_static_file("index.html")

@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save input
    filename = secure_filename(file.filename)
    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
    file.save(input_path)
    logging.info(f"Saved uploaded file: {input_path}")

    # Prepare output folder
    output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
    os.makedirs(output_folder, exist_ok=True)

    try:
        logging.info("Starting separation...")
        separator.separate_to_file(input_path, output_folder)
        logging.info("Separation complete ✅")

        base_name = os.path.splitext(filename)[0]
        result_folder = os.path.join(output_folder, base_name)

        vocals = os.path.join(result_folder, "vocals.wav")
        accompaniment = os.path.join(result_folder, "accompaniment.wav")

        if not os.path.exists(vocals) or not os.path.exists(accompaniment):
            raise FileNotFoundError("Separated files not found.")

        return jsonify({
            "message": "Separation complete ✅",
            "vocals": f"{uid}_output/{base_name}/vocals.wav",
            "accompaniment": f"{uid}_output/{base_name}/accompaniment.wav"
        })

    except Exception as e:
        logging.exception("Error during separation")
        return jsonify({"error": f"Could not process file: {str(e)}"}), 500


@app.route("/download/<path:filename>")
def download(filename):
    directory = os.path.join(UPLOAD_FOLDER)
    return send_from_directory(directory, filename, as_attachment=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
