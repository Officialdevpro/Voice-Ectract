import os
import subprocess
from flask import Flask, request, jsonify, send_file
import librosa
import soundfile as sf
import noisereduce as nr
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def convert_webm_to_wav(input_path, output_path):
    """Convert .webm to .wav using FFmpeg."""
    try:
        ffmpeg_cmd = [
            "C:\\ffmpeg", "-i", input_path, 
            "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", output_path, "-y"
        ]
        print("Running FFmpeg:", " ".join(ffmpeg_cmd))
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Conversion successful: {input_path} → {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        raise Exception("FFmpeg conversion failed.")

@app.route('/process-audio', methods=['POST'])
def process_audio():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(input_path)

        if not os.path.exists(input_path):
            return jsonify({"error": "Uploaded file not found"}), 400
        
        print(f"File saved at: {input_path}")

        # Convert WebM to WAV
        wav_path = os.path.join(app.config['UPLOAD_FOLDER'], "converted_audio.wav")
        convert_webm_to_wav(input_path, wav_path)

        # Load the audio file
        audio, sr = librosa.load(wav_path, sr=None)
        print("Audio loaded. Sample rate:", sr)

        # Perform noise reduction (keeping voice intact)
        reduced_noise_audio = nr.reduce_noise(y=audio, sr=sr, prop_decrease=1.0, stationary=True)
        print("Noise reduction completed.")

        # Save the processed audio
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'processed_audio.wav')
        sf.write(output_path, reduced_noise_audio, sr)
        print(f"Processed audio saved at: {output_path}")

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
