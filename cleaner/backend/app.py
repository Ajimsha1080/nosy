from flask import Flask, request, jsonify
from separate_audio import separate_audio  # Your audio separation function

app = Flask(__name__)

@app.route("/separate", methods=["POST"])
def separate():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]

    try:
        vocals_path, background_path = separate_audio(file)
        return jsonify({
            "vocals_url": f"/{vocals_path}",
            "background_url": f"/{background_path}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
