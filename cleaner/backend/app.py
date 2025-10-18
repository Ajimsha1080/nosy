from flask import Flask, request, jsonify
from spleeter.separator import Separator
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "separated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/separate", methods=["POST"])
def separate_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        separator = Separator("spleeter:2stems")
        separator.separate_to_file(filepath, OUTPUT_FOLDER)

        vocals_file = os.path.join(OUTPUT_FOLDER, file.filename.replace(".mp3", "/vocals.wav"))
        music_file = os.path.join(OUTPUT_FOLDER, file.filename.replace(".mp3", "/accompaniment.wav"))

        return jsonify({
            "vocals": vocals_file,
            "accompaniment": music_file,
            "message": "Separation complete!"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
