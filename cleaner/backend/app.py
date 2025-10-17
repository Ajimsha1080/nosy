import os
import uuid
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
FRONTEND_FOLDER = os.path.join(BASE_DIR, "../../frontend")

# Ensure directories exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Load Spleeter model once (2stems: vocals + accompaniment)
separator = Separator("spleeter:2stems")

logging.basicConfig(level=logging.INFO)

# Serve frontend
@app.route("/")
def serve_frontend():
    index_path = os.path.join(FRONTEND_FOLDER, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(FRONTEND_FOLDER, "index.html")
    return "Frontend not found. Check folder structure.", 404


# File upload + separation
@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save file with unique name
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}_{file.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    logging.info(f"Saved uploaded file: {input_path}")
    logging.info("Starting separation...")

    try:
        output_dir = os.path.join(OUTPUT_FOLDER, unique_id)
        os.makedirs(output_dir, exist_ok=True)
        separator.separate_to_file(input_path, output_dir)

        vocals_path = os.path.join(output_dir, "vocals.wav")
        accomp_path = os.path.join(output_dir, "accompaniment.wav")

        if not (os.path.exists(vocals_path) and os.path.exists(accomp_path)):
            raise FileNotFoundError("Separated files not found")

        return jsonify({
            "message": "Separation completed successfully!",
            "vocals": f"{unique_id}/vocals.wav",
            "accompaniment": f"{unique_id}/accompaniment.wav"
        })

    except Exception as e:
        logging.error(f"Error during separation: {e}")
        return jsonify({"error": str(e)}), 500


# Serve separated files
@app.route("/download/<path:filename>")
def download_file(filename):
    folder = OUTPUT_FOLDER
    return send_from_directory(folder, filename, as_attachment=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
