from flask import Flask, request, jsonify, send_file
import os
import uuid
import logging

# Import your audio separation function
# from cleaner.separation import separate_audio_function
# Replace with your actual function

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "/tmp/uploads"
OUTPUT_FOLDER = "/tmp/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_audio(input_path):
    """
    Replace this with your actual separation logic.
    It should return paths to vocals and accompaniment files.
    """
    # Example: using input filename to create outputs
    base = os.path.splitext(os.path.basename(input_path))[0]
    vocals_file = os.path.join(OUTPUT_FOLDER, f"{base}_vocals.wav")
    accompaniment_file = os.path.join(OUTPUT_FOLDER, f"{base}_accompaniment.wav")

    # Here, call your real separation function
    # Example:
    # separate_audio_function(input_path, vocals_file, accompaniment_file)

    # For now, just copy input as dummy output
    import shutil
    shutil.copy(input_path, vocals_file)
    shutil.copy(input_path, accompaniment_file)

    return vocals_file, accompaniment_file


@app.route("/")
def home():
    return """
    <h2>Welcome to the Audio Separation API!</h2>
    <p>Upload an audio file to separate vocals and accompaniment.</p>
    <form action="/separate" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".mp3,.wav,.ogg" required>
        <input type="submit" value="Upload & Separate">
    </form>
    """

@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded file
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{file.filename}")
    file.save(input_path)
    logging.info(f"Processing: {file.filename}")

    try:
        vocals_path, accompaniment_path = process_audio(input_path)

        # Return paths for download (you may want to serve static files properly)
        return jsonify({
            "vocals": f"/download/{os.path.basename(vocals_path)}",
            "accompaniment": f"/download/{os.path.basename(accompaniment_path)}",
            "message": "Separation complete ✅"
        })

    except Exception as e:
        logging.exception("Error during audio separation")
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
