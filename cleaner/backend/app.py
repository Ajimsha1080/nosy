import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from spleeter.separator import Separator

app = Flask(__name__, static_folder="../frontend")
CORS(app)

# Create upload and output directories if not exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Initialize Spleeter (2 stems: vocals + accompaniment)
separator = Separator("spleeter:2stems", multiprocess=False)

@app.route("/")
def home():
    # Serve the frontend
    return send_from_directory(app.static_folder, "index.html")

@app.route("/separate", methods=["POST"])
def separate_audio():
    try:
        # Validate uploaded file
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Save uploaded file
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        input_path = os.path.join("uploads", unique_name)
        file.save(input_path)

        # Output folder for separated files
        output_dir = os.path.join("output", unique_name.split(".")[0])
        os.makedirs(output_dir, exist_ok=True)

        # Run Spleeter separation
        separator.separate_to_file(input_path, "output")

        # Define expected paths
        vocals_path = os.path.join(output_dir, "vocals.wav")
        accompaniment_path = os.path.join(output_dir, "accompaniment.wav")

        # Check files exist
        if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
            return jsonify({"error": "Separation failed"}), 500

        return jsonify({
            "message": "✅ Separation complete!",
            "vocals": f"{unique_name.split('.')[0]}/vocals.wav",
            "accompaniment": f"{unique_name.split('.')[0]}/accompaniment.wav"
        })
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/download/<path:filename>")
def download_file(filename):
    # Serve files from output folder
    return send_from_directory("output", filename, as_attachment=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
