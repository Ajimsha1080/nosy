from flask import Flask, request, jsonify, send_file, render_template
from spleeter.separator import Separator
import os
import tempfile
import logging

# Setup logging (Render will capture this)
logging.basicConfig(level=logging.INFO)

# Flask app setup
app = Flask(__name__, template_folder="templates", static_folder="static")

# Spleeter separator (2 stems: vocals + accompaniment)
separator = Separator('spleeter:2stems')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/separate", methods=["POST"])
def separate_audio():
    # Check file field
    if "file" not in request.files:
        logging.error("No file part in request")
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        logging.error("Empty filename")
        return jsonify({"error": "No selected file"}), 400

    # Create temp dirs
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, file.filename)
    file.save(input_path)

    output_dir = os.path.join(temp_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Separate audio
        separator.separate_to_file(input_path, output_dir)

        # Collect separated files
        separated_files = {}
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                separated_files[f] = os.path.join(root, f)

        logging.info(f"Separation done for {file.filename}")
        return jsonify({
            "message": "Separation complete ✅",
            "files": list(separated_files.keys())
        })

    except Exception as e:
        logging.exception("Error during separation")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    # Serve separated files
    for root, dirs, files in os.walk(tempfile.gettempdir()):
        if filename in files:
            return send_file(os.path.join(root, filename), as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    # Important for Render — must bind to 0.0.0.0 and port 10000 if set
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
