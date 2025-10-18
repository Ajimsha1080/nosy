from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Root route serves frontend
@app.route("/")
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files (like JS, CSS) if needed
@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

# Audio separation endpoint
@app.route("/separate", methods=["POST"])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename
    save_path = os.path.join("uploads", filename)

    os.makedirs("uploads", exist_ok=True)
    file.save(save_path)

    # --- AUDIO SEPARATION LOGIC ---
    # Replace the following with your actual separation function
    vocals_url = f"/uploads/vocals_{filename}"
    background_url = f"/uploads/background_{filename}"

    # For testing: just copy the original file as both vocals & background
    import shutil
    shutil.copy(save_path, f".{vocals_url}")
    shutil.copy(save_path, f".{background_url}")

    return jsonify({
        "vocals_url": vocals_url,
        "background_url": background_url
    })

# Serve uploaded files
@app.route("/uploads/<path:filename>")
def uploaded_files(filename):
    return send_from_directory("uploads", filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
