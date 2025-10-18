from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from separate_audio import separate_audio
import os

app = Flask(__name__)
CORS(app)  # allow cross-origin requests from Netlify frontend

@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    vocals_path, instrumental_path = separate_audio(file)

    # Return URLs for frontend to download
    # On Render, you can use '/download/<filename>' route to serve files
    vocals_url = f"/download/{os.path.basename(vocals_path)}"
    instrumental_url = f"/download/{os.path.basename(instrumental_path)}"
    return jsonify({"vocals_url": vocals_url, "background_url": instrumental_url})

@app.route("/download/<filename>")
def download_file(filename):
    # Serve file from UPLOAD_FOLDER
    for root, dirs, files in os.walk("/tmp/audio_files"):
        if filename in files:
            return send_file(os.path.join(root, filename))
    return "File not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
