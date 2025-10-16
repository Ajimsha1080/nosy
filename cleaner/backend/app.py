import os
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
from spleeter.separator import Separator

# Disable GPU since Render doesn't have CUDA
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Initialize Flask
app = Flask(__name__)

# Initialize Spleeter for 2-stem separation (vocals + accompaniment)
separator = Separator('spleeter:2stems')

# Simple HTML page (no need for templates folder)
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Audio Separation API</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; margin-top: 60px; }
    input, button { padding: 10px; margin-top: 20px; font-size: 16px; }
    button { cursor: pointer; background-color: #4CAF50; color: white; border: none; }
    button:hover { background-color: #45a049; }
  </style>
</head>
<body>
  <h1>Welcome to the Audio Separation API!</h1>
  <p>Upload an audio file to separate its vocals and background.</p>
  <form id="uploadForm" enctype="multipart/form-data" method="POST" action="/separate">
    <input type="file" name="audio" accept="audio/*" required>
    <br>
    <button type="submit">Upload & Separate</button>
  </form>
  <div id="result"></div>
  <script>
    const form = document.getElementById('uploadForm');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      document.getElementById('result').innerHTML = "Processing...";
      try {
        const res = await fetch('/separate', { method: 'POST', body: formData });
        const data = await res.json();
        if (res.ok) {
          document.getElementById('result').innerHTML =
            `<p>✅ Separation complete!</p><pre>${JSON.stringify(data, null, 2)}</pre>`;
        } else {
          document.getElementById('result').innerHTML = `<p>❌ Error: ${data.error}</p>`;
        }
      } catch (err) {
        document.getElementById('result').innerHTML = `<p>❌ Network error</p>`;
      }
    });
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/separate', methods=['POST'])
def separate_audio():
    # Ensure a file is uploaded
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']
    filename = secure_filename(audio_file.filename)
    if not filename:
        return jsonify({'error': 'Invalid filename'}), 400

    # Temporary paths (Render allows writing to /tmp)
    input_path = os.path.join('/tmp', filename)
    output_dir = os.path.join('/tmp', 'output')

    os.makedirs(output_dir, exist_ok=True)
    audio_file.save(input_path)

    try:
        # Run spleeter
        separator.separate_to_file(input_path, output_dir)

        # Find results
        output_files = []
        for root, _, files in os.walk(output_dir):
            for f in files:
                output_files.append(f"/download/{f}")

        return jsonify({'message': 'Separation complete', 'files': output_files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    file_path = os.path.join('/tmp', 'output', 'audio', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
