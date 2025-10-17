import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from spleeter.separator import Separator

app = Flask(__name__)

# Folder to store uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Spleeter 2-stems separator (vocals + accompaniment)
separator = Separator('spleeter:2stems')

# ------------------ FRONTEND ------------------
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎵 Audio Separation API</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; text-align: center; background: #f7f8fa; }
button { padding: 12px 24px; font-size: 16px; border-radius: 8px; cursor: pointer; background: #0078ff; color: white; border: none; }
button:hover { background: #005fcc; }
audio { display: block; margin: 10px auto; width: 80%; max-width: 400px; }
a { display: block; margin-bottom: 20px; color: #0078ff; text-decoration: none; }
a:hover { text-decoration: underline; }
#status { margin-top: 20px; font-weight: bold; }
.card { background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); max-width: 500px; margin: 20px auto; }
</style>
</head>
<body>
<h1>🎵 Audio Separation API</h1>
<p>Upload your song to extract vocals and background music.</p>

<div class="card">
    <input type="file" id="fileInput" accept="audio/*"><br><br>
    <button onclick="uploadFile()">Upload & Separate</button>
</div>

<div id="status"></div>
<div id="result"></div>

<script>
async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) {
        alert("Please select an audio file first.");
        return;
    }
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("status").innerText = "⏳ Uploading and processing, please wait...";
    document.getElementById("result").innerHTML = "";

    try {
        const res = await fetch("/separate", { method: "POST", body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Server error");

        document.getElementById("status").innerText = data.message;

        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = `
            <h3>🎤 Vocals</h3>
            <audio controls src="/download/${data.vocals}"></audio>
            <a href="/download/${data.vocals}" download>⬇️ Download Vocals</a>

            <h3>🎶 Accompaniment</h3>
            <audio controls src="/download/${data.accompaniment}"></audio>
            <a href="/download/${data.accompaniment}" download>⬇️ Download Background</a>
        `;
    } catch (err) {
        console.error(err);
        document.getElementById("status").innerText = `❌ Error: ${err.message}`;
    }
}
</script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(FRONTEND_HTML)

# ------------------ AUDIO SEPARATION ------------------
@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = secure_filename(file.filename)
        uid = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{uid}_{filename}")
        file.save(input_path)

        # Folder for output
        output_folder = os.path.join(UPLOAD_FOLDER, f"{uid}_output")
        os.makedirs(output_folder, exist_ok=True)

        # Perform separation
        separator.separate_to_file(input_path, output_folder)

        # Paths to separated files
        base_name = os.path.splitext(filename)[0]
        vocals_path = os.path.join(output_folder, base_name, "vocals.wav")
        accompaniment_path = os.path.join(output_folder, base_name, "accompaniment.wav")

        if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
            return jsonify({"error": "Separation failed"}), 500

        # Return just the filenames for frontend
        return jsonify({
            "message": "✅ Separation complete!",
            "vocals": f"{uid}_output/{base_name}/vocals.wav",
            "accompaniment": f"{uid}_output/{base_name}/accompaniment.wav"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ DOWNLOAD ------------------
@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=False)
    else:
        return jsonify({"error": "File not found"}), 404

# ------------------ RUN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
