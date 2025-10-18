from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from cleaner import separate_audio  # Your audio separation function

app = Flask(__name__)
CORS(app)  # allow requests from frontend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/separate", methods=["POST"])
def separate():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        vocals_url, background_url = separate_audio(filepath)
        return jsonify({
            "vocals_url": vocals_url,
            "background_url": background_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
