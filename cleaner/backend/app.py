import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

UPLOAD_FOLDER = "uploads"
SEPARATED_FOLDER = "separated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SEPARATED_FOLDER, exist_ok=True)

separator = Separator('spleeter:2stems', multiprocess=False)

# Serve frontend
@app.route("/")
def index():
    return app.send_static_file("index.html")

# Audio separation endpoint
@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    ext = file.filename.rsplit('.', 1)[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(file_path)

    try:
        output_dir = os.path.join(SEPARATED_FOLDER, str(uuid.uuid4()))
        os.makedirs(output_dir, exist_ok=True)
        separator.separate_to_file(file_path, output_dir)

        vocals_file = os.path.join(output_dir, "vocals.wav")
        acc_file = os.path.join(output_dir, "accompaniment.wav")

        return jsonify({
            "message": "Separation complete!",
            "vocals": vocals_file,
            "accompaniment": acc_file
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve separated files
@app.route("/download/<path:filename>")
def download_file(filename):
    directory = os.path.dirname(filename)
    filename_only = os.path.basename(filename)
    return send_from_directory(directory, filename_only, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
