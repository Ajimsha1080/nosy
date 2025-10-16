import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import logging

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Setup upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed audio extensions
ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Homepage route
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Audio separation route
@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        logging.info(f"Processing: {filename}")

        # --- Audio separation logic ---
        # Replace this with your actual separation function
        vocals_path = filepath.replace(".mp3", "_vocals.wav")
        accompaniment_path = filepath.replace(".mp3", "_accompaniment.wav")

        # Dummy response for now (replace with real output paths)
        response = {
            "message": "Separation complete ✅",
            "vocals": vocals_path,
            "accompaniment": accompaniment_path
        }
        return jsonify(response), 200

    return jsonify({"error": "File type not allowed"}), 400

# Route to serve uploaded/downloaded files
@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
