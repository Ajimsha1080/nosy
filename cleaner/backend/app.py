import os
import uuid
import logging
from flask import Flask, request, jsonify, send_file, render_template
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

# -------------------------
# Logging
logging.basicConfig(level=logging.INFO)

# -------------------------
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# Initialize Spleeter (CPU-only)
separator = Separator('spleeter:2stems', multiprocess=False)

# -------------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# -------------------------
@app.route("/separate", methods=["POST"])
def separate():
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

    # Perform separation
    logging.info("Starting separation...")
    separator.separate_to_file(input_path, output_folder)
    logging.info("Separation finished!")

    # The output folder structure is: output_folder/{basename}/
    base_name = filename.rsplit(".", 1)[0]
    base_dir = os.path.join(output_folder, base_name)

    vocals_path = os.path.join(base_dir, "vocals.wav")
    accompaniment_path = os.path.join(base_dir, "accompaniment.wav")

    if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
        logging.error("Output files not found after separation!")
        return jsonify({"error": "Separation failed"}), 500

    # Return relative paths for frontend download/play
    return jsonify({
        "message": "Separation complete ✅",
        "vocals": os.path.relpath(vocals_path, start=UPLOAD_FOLDER),
        "accompaniment": os.path.relpath(accompaniment_path, start=UPLOAD_FOLDER)
    })

# -------------------------
@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
