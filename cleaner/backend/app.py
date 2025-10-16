import os
import uuid
from flask import Flask, request, jsonify, send_file
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems')

@app.route("/", methods=["GET"])
def home():
    return "Audio Separation API is live!"

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

    output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
    os.makedirs(output_folder, exist_ok=True)

    # Separate audio
    separator.separate_to_file(input_path, output_folder)

    # Get output paths
    base_name = filename.rsplit(".", 1)[0]  # without extension
    vocals_path = os.path.join(output_folder, base_name, "vocals.wav")
    accompaniment_path = os.path.join(output_folder, base_name, "accompaniment.wav")

    if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
        return jsonify({"error": "Separation failed"}), 500

    # Return URLs for frontend
    return jsonify({
        "message": "Separation complete ✅",
        "vocals_url": f"/download/{uid}_output/{base_name}/vocals.wav",
        "accompaniment_url": f"/download/{uid}_output/{base_name}/accompaniment.wav"
    })

@app.route("/download/<path:filepath>", methods=["GET"])
def download(filepath):
    full_path = os.path.join(UPLOAD_FOLDER, filepath)
    if os.path.exists(full_path):
        return send_file(full_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
