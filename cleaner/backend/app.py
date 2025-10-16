from flask import Flask, request, jsonify, send_from_directory, render_template
import os

app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy separation function (replace with your real separation code)
def separate_audio(file_path):
    base = os.path.splitext(os.path.basename(file_path))[0]
    vocals = os.path.join(UPLOAD_FOLDER, f"{base}_vocals.wav")
    accompaniment = os.path.join(UPLOAD_FOLDER, f"{base}_accompaniment.wav")

    # Replace this block with your actual separation logic
    # For testing, just copy original file as both outputs
    import shutil
    shutil.copyfile(file_path, vocals)
    shutil.copyfile(file_path, accompaniment)

    return vocals, accompaniment

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/separate', methods=['POST'])
def separate():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    vocals_path, accompaniment_path = separate_audio(filepath)

    # Convert to URLs relative to static path
    vocals_url = f"/uploads/{os.path.basename(vocals_path)}"
    accompaniment_url = f"/uploads/{os.path.basename(accompaniment_path)}"

    return jsonify({
        "vocals": vocals_url,
        "accompaniment": accompaniment_url,
        "message": "Separation complete ✅"
    })

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
