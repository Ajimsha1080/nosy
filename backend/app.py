import os
import io
import base64
import subprocess
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment

# ------------------------------
# Initialize Flask app and CORS
# ------------------------------
app = Flask(__name__)
CORS(app)  # Allow all origins (frontend <-> backend)

# Folder to store uploaded files temporarily
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ------------------------------
# Route: Separate Audio
# ------------------------------
@app.route('/separate', methods=['POST'])
def separate_audio():
    """
    Separates vocals and accompaniment from an uploaded audio file using Spleeter.
    Returns both tracks as base64-encoded WAV files.
    """
    try:
        # ------------------------------
        # 1. Check for uploaded file
        # ------------------------------
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio_file']

        if audio_file.filename == "":
            return jsonify({'error': 'Empty filename'}), 400

        # ------------------------------
        # 2. Save the uploaded file safely
        # ------------------------------
        safe_filename = audio_file.filename.replace(" ", "_").replace("(", "").replace(")", "")
        temp_dir = f"temp_spleeter_{os.getpid()}"
        os.makedirs(temp_dir, exist_ok=True)
        temp_input_path = os.path.join(temp_dir, safe_filename)
        audio_file.save(temp_input_path)
        print("Saved input file at:", temp_input_path)

        # ------------------------------
        # 3. Define output directory
        # ------------------------------
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)

        # ------------------------------
        # 4. Run Spleeter
        # ------------------------------
        command = [
            'spleeter', 'separate',
            '-p', 'spleeter:2stems',
            '-o', output_dir,
            '-i', temp_input_path
        ]

        process = subprocess.run(command, capture_output=True, text=True)

        if process.returncode != 0:
            print("Spleeter command failed:")
            print("Stdout:", process.stdout)
            print("Stderr:", process.stderr)
            return jsonify({'error': 'Spleeter processing failed', 'details': process.stderr}), 500

        # ------------------------------
        # 5. Load separated audio
        # ------------------------------
        output_subdir = os.path.join(output_dir, os.path.splitext(safe_filename)[0])
        vocals_path = os.path.join(output_subdir, 'vocals.wav')
        accompaniment_path = os.path.join(output_subdir, 'accompaniment.wav')

        if not os.path.exists(vocals_path) or not os.path.exists(accompaniment_path):
            return jsonify({'error': 'Spleeter output files not found. Check input format.'}), 500

        # Convert to base64
        vocals_audio = AudioSegment.from_wav(vocals_path)
        accompaniment_audio = AudioSegment.from_wav(accompaniment_path)

        vocals_stream = io.BytesIO()
        accompaniment_stream = io.BytesIO()
        vocals_audio.export(vocals_stream, format="wav")
        accompaniment_audio.export(accompaniment_stream, format="wav")

        vocals_base64 = base64.b64encode(vocals_stream.getvalue()).decode('utf-8')
        accompaniment_base64 = base64.b64encode(accompaniment_stream.getvalue()).decode('utf-8')

        # ------------------------------
        # 6. Cleanup
        # ------------------------------
        shutil.rmtree(temp_dir)

        # ------------------------------
        # 7. Return JSON response
        # ------------------------------
        return jsonify({
            'vocals': vocals_base64,
            'accompaniment': accompaniment_base64
        })

    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({'error': str(e)}), 500


# ------------------------------
# Main block for local testing
# UPDATED: For Render deployment
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
