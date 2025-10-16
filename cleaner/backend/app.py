import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator

# Absolute path for Render environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

# Create folders
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

separator = Separator("spleeter:2stems", multiprocess=False)

@app.route("/")
def home():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return "Frontend not found. Check folder structure.", 404
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/separate", methods=["POST"])
def separate_audio():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        unique_name = f"{uuid.uuid4()}_{file.filename}"
        input_path = os.path.join("uploads", unique_name)
        file.save(input_path)

        output_dir = os.path.join("output", unique_name.split(".")[0])
        os.makedirs(output_dir, exist_ok=True)

        separator.separate_to_file(input_path, "output")

        vocals_path = os.path.join(output_dir, "vocals.wav")
        accompaniment_path = os.path.join(output_dir, "accompaniment.wav")

        if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
            return jsonify({"error": "Separation failed"}), 500

        return jsonify({
            "message": "✅ Separation complete!",
            "vocals": f"{unique_name.split('.')[0]}/vocals.wav",
            "accompaniment": f"{unique_name.split('.')[0]}/accompaniment.wav"
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory("output", filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
