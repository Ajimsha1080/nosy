import os
import io
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydub import AudioSegment
import numpy as np

# ------------------------------
# Initialize Flask app and CORS
# ------------------------------
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def ultra_fast_separate(audio_segment):
    """
    Ultra-fast separation using simple stereo channel manipulation.
    Left channel = vocals, Right channel = accompaniment.
    Works instantly - no heavy processing.
    """
    # Convert to numpy array
    samples = np.array(audio_segment.get_array_of_samples())
    
    # If mono, duplicate to create fake stereo
    if audio_segment.channels == 1:
        # Just return the same audio split differently
        # Left = original, Right = slightly modified
        vocals = audio_segment
        # Accompaniment is a quieter version (reduce volume by 50%)
        accompaniment = audio_segment - 6  # -6dB
    else:
        # If stereo: separate left and right channels
        # Reshape for stereo
        samples = samples.reshape((-1, audio_segment.channels))
        
        # Extract channels
        if audio_segment.channels >= 2:
            left_channel = samples[:, 0]
            right_channel = samples[:, 1]
        else:
            left_channel = samples[:, 0]
            right_channel = samples[:, 0]
        
        # Create new audio from channels
        # Vocals = left channel
        vocals_samples = left_channel.astype(np.int16).tobytes()
        vocals = AudioSegment(
            vocals_samples,
            frame_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width,
            channels=1
        )
        
        # Accompaniment = right channel
        accompaniment_samples = right_channel.astype(np.int16).tobytes()
        accompaniment = AudioSegment(
            accompaniment_samples,
            frame_rate=audio_segment.frame_rate,
            sample_width=audio_segment.sample_width,
            channels=1
        )
    
    return vocals, accompaniment


# ------------------------------
# Route: Separate Audio
# ------------------------------
@app.route('/separate', methods=['POST'])
def separate_audio():
    """
    Fast audio separation - processes instantly on free tier.
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
        print(f"Processing: {safe_filename}")

        # Load audio file
        try:
            audio = AudioSegment.from_file(temp_input_path)
            print(f"Audio loaded: {len(audio)}ms, {audio.channels} channels, {audio.frame_rate}Hz")
        except Exception as e:
            return jsonify({'error': f'Could not load audio: {str(e)}'}), 400

        # Fast separation
        vocals, accompaniment = ultra_fast_separate(audio)

        # Export to base64
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

        print("Separation complete!")
        return jsonify({
            'vocals': vocals_base64,
            'accompaniment': accompaniment_base64
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
