import os
import uuid
from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from spleeter.separator import Separator
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow frontend JS to call backend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Spleeter (vocals + accompaniment)
separator = Separator('spleeter:2stems')

@app.route("/", methods=["GET"])
def home():
    return "Audio Separation API is live!"

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
        print(f"Saved uploaded file: {input_path}")

        # Output folder
        output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
        os.makedirs(output_folder, exist_ok=True)

        print("Starting separation...")
        separator.separate_to_file(input_path, output_folder)
        print("Separation done!")

        # Separated files
        base_name = filename.replace(".mp3", "")
        vocals_path = os.path.join(output_folder, base_name, "vocals.wav")
        accompaniment_path = os.path.join(output_folder, base_name, "accompaniment.wav")

        if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
            return jsonify({"error": "Separation failed"}), 500

        # Return relative paths for frontend
        return jsonify({
            "message": "Separation complete ✅",
            "vocals": os.path.relpath(vocals_path, UPLOAD_FOLDER),
            "accompaniment": os.path.relpath(accompaniment_path, UPLOAD_FOLDER)
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500


@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"File not found: {str(e)}"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
