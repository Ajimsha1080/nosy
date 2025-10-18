from flask import Flask, request, jsonify
from flask_cors import CORS
from cleaner.separate_audio import separate_audio

app = Flask(__name__)
CORS(app)  # Allow frontend (Netlify) to call backend

@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    audio_file = request.files["file"]
    
    try:
        vocals_url, background_url = separate_audio(audio_file)
        return jsonify({
            "vocals_url": vocals_url,
            "background_url": background_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
