from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Set the upload folder (ensure it's correct)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the audio file (e.g., using some library like pydub or ffmpeg)
        try:
            # Example: use pydub to process the audio file
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(filepath)
            processed_file_path = filepath.rsplit('.', 1)[0] + '_processed.wav'
            audio.export(processed_file_path, format="wav")

            # Return the processed file
            return send_file(processed_file_path, as_attachment=True, mimetype='audio/wav')
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(debug=True)
