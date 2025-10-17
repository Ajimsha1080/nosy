import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# === Flask setup ===
app = Flask(__name__)
CORS(app)

# === Directories ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# === Home route ===
@app.route("/")
def home():
    return "<h2>🎵 Audio Separation API is Live!</h2><p>Use POST /separate to process audio files.</p>"


# === Audio Separation Route ===
@app.route("/separate", methods=["POST"])
def separate_audio():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        saved_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{filename}")
        file.save(saved_path)
        app.logger.info(f"Saved uploaded file: {saved_path}")

        # Simulate processing (replace with your ML separation logic)
        vocals_filename = f"{unique_id}_vocals.wav"
        accompaniment_filename = f"{unique_id}_background.wav"

        vocals_path = os.path.join(OUTPUT_FOLDER, vocals_filename)
        accompaniment_path = os.path.join(OUTPUT_FOLDER, accompaniment_filename)

        # Dummy copy (simulate output)
        with open(saved_path, "rb") as src:
            data = src.read()
            with open(vocals_path, "wb") as v:
                v.write(data)
            with open(accompaniment_path, "wb") as a:
                a.write(data)

        return jsonify({
            "message": "✅ Separation complete!",
            "vocals": vocals_filename,
            "accompaniment": accompaniment_filename
        })

    except Exception as e:
        app.logger.error(f"Error during separation: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# === Download Route ===
@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    try:
        # Serve from OUTPUT_FOLDER
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


# === Start server locally ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
