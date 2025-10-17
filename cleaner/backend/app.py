import os
import uuid
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # allow frontend to make requests

# Folder to store uploaded and separated audio
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Spleeter 2-stems separator (vocals + accompaniment)
separator = Separator('spleeter:2stems')

@app.route("/", methods=["GET"])
def home():
    return send_from_directory("../frontend", "index.html")  # serve frontend

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

    # Folder for output
    output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
    os.makedirs(output_folder, exist_ok=True)

    try:
        separator.separate_to_file(input_path, output_folder)
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

    # Construct paths for frontend download
    vocals_path = os.path.join(f"{uid}_output", filename.replace(".mp3", ""), "vocals.wav")
    accompaniment_path = os.path.join(f"{uid}_output", filename.replace(".mp3", ""), "accompaniment.wav")

    return jsonify({
        "message": "✅ Separation complete!",
        "vocals": vocals_path,
        "accompaniment": accompaniment_path
    })

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    # Serve file from uploads folder
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
