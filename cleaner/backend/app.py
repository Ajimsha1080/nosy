import os
import uuid
import base64
from flask import Flask, request, jsonify
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    filename = secure_filename(file.filename)
    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
    file.save(input_path)

    output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
    os.makedirs(output_folder, exist_ok=True)

    try:
        separator.separate_to_file(input_path, output_folder)
    except Exception as e:
        return jsonify({"error": f"Separation failed: {str(e)}"}), 500

    vocals_path = os.path.join(output_folder, filename.replace(".mp3", ""), "vocals.wav")
    accompaniment_path = os.path.join(output_folder, filename.replace(".mp3", ""), "accompaniment.wav")

    def to_base64(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    try:
        vocals_b64 = to_base64(vocals_path)
        accompaniment_b64 = to_base64(accompaniment_path)
    except Exception as e:
        return jsonify({"error": f"Failed to read output files: {str(e)}"}), 500

    return jsonify({
        "message": "Separation complete ✅",
        "vocals": vocals_b64,
        "accompaniment": accompaniment_b64
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
