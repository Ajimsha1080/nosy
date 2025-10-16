from flask import Flask, request, jsonify, send_file, render_template
import os
import tempfile
import traceback
import logging

# Try to import Spleeter safely
try:
    from spleeter.separator import Separator
    separator = Separator('spleeter:2stems')
except Exception as e:
    separator = None
    print("⚠️ Warning: Spleeter could not be initialized:", e)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/separate", methods=["POST"])
def separate_audio():
    """Handle uploaded audio and separate vocals/accompaniment."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Make sure spleeter is ready
        if not separator:
            return jsonify({"error": "Spleeter not initialized on server"}), 500

        # Save file
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, file.filename)
        file.save(input_path)

        # Prepare output folder
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        logging.info(f"Processing: {file.filename}")
        separator.separate_to_file(input_path, output_dir)

        # Collect results
        separated_files = []
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                separated_files.append(f)

        return jsonify({
            "message": "Separation complete ✅",
            "files": separated_files
        })

    except Exception as e:
        error_message = f"Server crash: {str(e)}"
        logging.error(error_message)
        traceback.print_exc()
        return jsonify({"error": error_message}), 500


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Serve separated files if available."""
    for root, dirs, files in os.walk(tempfile.gettempdir()):
        if filename in files:
            return send_file(os.path.join(root, filename), as_attachment=True)
    return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Running on port {port}")
    app.run(host="0.0.0.0", port=port)
