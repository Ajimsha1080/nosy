import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Spleeter 2-stems separator
separator = Separator('spleeter:2stems')

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
    file.save(input_path)

    # Output folder
    output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
    os.makedirs(output_folder, exist_ok=True)

    # Perform separation
    try:
        separator.separate_to_file(input_path, output_folder)
    except Exception as e:
        return jsonify({"error": f"Separation failed: {str(e)}"}), 500

    # Get output file paths
    file_base = os.path.splitext(filename)[0]
    vocals_path = os.path.join(output_folder, file_base, "vocals.wav")
    accompaniment_path = os.path.join(output_folder, file_base, "accompaniment.wav")

    if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
        return jsonify({"error": "Separation failed"}), 500

    # Return relative paths for frontend
    return jsonify({
        "message": "Separation complete ✅",
        "vocals": f"/download/{uid}_output/{file_base}/vocals.wav",
        "accompaniment": f"/download/{uid}_output/{file_base}/accompaniment.wav"
    })


@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file_path = os.path.abspath(file_path)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
