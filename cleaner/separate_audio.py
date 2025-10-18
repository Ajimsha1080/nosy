import os
import uuid
from spleeter.separator import Separator
from werkzeug.utils import secure_filename

# Folder to store temporary audio files
UPLOAD_FOLDER = "/tmp/audio_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Spleeter 2-stems separator (vocals + accompaniment)
separator = Separator('spleeter:2stems')

def separate_audio(file):
    """
    Separate vocals and instrumental from an uploaded audio file.

    Args:
        file: FileStorage object from Flask

    Returns:
        vocals_url, background_url: URLs or paths to separated audio files
    """
    # Save uploaded file
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{filename}")
    file.save(input_path)

    # Output folder for separated files
    output_folder = os.path.join(UPLOAD_FOLDER, f"{unique_id}_output")
    os.makedirs(output_folder, exist_ok=True)

    # Run separation
    separator.separate_to_file(input_path, output_folder)

    # Spleeter output paths
    base_name = os.path.splitext(filename)[0]
    vocals_file = os.path.join(output_folder, base_name, "vocals.wav")
    instrumental_file = os.path.join(output_folder, base_name, "accompaniment.wav")

    # In Render, serve these files using /static or a cloud bucket
    # For now, return relative paths
    return vocals_file, instrumental_file

