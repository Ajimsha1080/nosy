import os
import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment
from pydub.effects import high_pass_filter, low_pass_filter

# ------------------------------
# Initialize Flask app and CORS
# ------------------------------
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Simple audio separation using frequency filtering
def simple_separate_audio(audio_segment):
    """
    Simple vocal/accompaniment separation using frequency filtering.
    Vocals are typically in higher frequencies, accompaniment in lower.
    """
    # High pass filter for vocals (frequencies above 2000 Hz)
    vocals = high_pass_filter(audio_segment, 2000)
    
    # Low pass filter for accompaniment (frequencies below 4000 Hz)
    accompaniment = low_pass_filter(audio_segment, 4000)
    
    return vocals, accompaniment


# ------------------------------
# Route: Separate Audio
# ------------------------------
@app.route('/separate', methods=['POST'])
def separate_audio():
    """
    Separates vocals and accompaniment from an uploaded audio file.
    Uses simple frequency-based filtering (lightweight alternative to Spleeter).
    """
    try:
        # Check for uploaded file
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio_file']

        if audio_file.filename == "":
            return jsonify({'error': 'Empty filename'}), 400

        # Save uploaded file
        safe_filename = audio_file.filename.replace(" ", "_").replace("(", "").replace(")", "")
        temp_input_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        audio_file.save(temp_input_path)
        print("Saved input file at:", temp_input_path)

        # Load audio file
        try:
            audio = AudioSegment.from_file(temp_input_path)
        except Exception as e:
            return jsonify({'error': f'Could not load audio file: {str(e)}'}), 400

        # Perform separation
        vocals, accompaniment = simple_separate_audio(audio)

        # Convert to WAV and encode as base64
        vocals_stream = io.BytesIO()
        accompaniment_stream = io.BytesIO()
        
        vocals.export(vocals_stream, format="wav")
        accompaniment.export(accompaniment_stream, format="wav")

        vocals_base64 = base64.b64encode(vocals_stream.getvalue()).decode('utf-8')
        accompaniment_base64 = base64.b64encode(accompaniment_stream.getvalue()).decode('utf-8')

        # Cleanup
        try:
            os.remove(temp_input_path)
        except:
            pass

        return jsonify({
            'vocals': vocals_base64,
            'accompaniment': accompaniment_base64
        })

    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({'error': str(e)}), 500


# ------------------------------
# Health check endpoint
# ------------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


# ------------------------------
# Main block
# ------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
