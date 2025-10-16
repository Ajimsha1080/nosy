import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from some_audio_separation_module import separate_audio  # Replace with your separation logic

app = Flask(__name__)
UPLOAD_FOLDER = "temp"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/separate", methods=["POST"])
def separate():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files["audio"]
    filename = secure_filename(file.filename)
    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
    file.save(input_path)

    # Separate audio
    vocals_path, accompaniment_path = separate_audio(input_path, uid, UPLOAD_FOLDER)

    return jsonify({
        "message": "Separation complete ✅",
        "vocals": f"/download/{os.path.basename(vocals_path)}",
        "accompaniment": f"/download/{os.path.basename(accompaniment_path)}"
    })

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
