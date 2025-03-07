import numpy as np
import librosa
import sys
import json

def extract_audio_features(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)

        if len(y.shape) > 1:
            y = librosa.to_mono(y)

        # Extract pitch as an array (without averaging)
        pitch, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        
        # Replace NaN values with None (or 0.0 if you prefer)
        pitch = [round(float(p), 2) if not np.isnan(p) else None for p in pitch]

        # Debug: Check if pitch array is all None
        if all(p is None for p in pitch):
            print("Warning: Pitch estimation failed. All values are None.", file=sys.stderr)

        # Extract amplitude as an array (without averaging)
        amplitude = [round(float(np.sqrt(sample ** 2)), 4) for sample in y]

        # Extract dominant frequencies as an array (without averaging)
        fft_spectrum = np.abs(np.fft.rfft(y))
        freqs = np.fft.rfftfreq(len(y), 1 / sr)
        dominant_freqs = [round(float(freqs[i]), 2) for i in range(len(fft_spectrum))]

        # Extract tempo (this remains a single value)
        tempo_array, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = round(float(tempo_array[0]), 2) if len(tempo_array) > 0 else None

        # Prepare the result with arrays instead of averages
        result = {
            "pitch": pitch,
            "amplitude": amplitude,
            "dominant_frequencies": dominant_freqs,
            "tempo": tempo
        }
        print(json.dumps(result))  # Always output valid JSON
    except Exception as e:
        print(json.dumps({"error": str(e)}))  # Ensure JSON is always returned

if __name__ == '__main__':
    if len(sys.argv) > 1:
        extract_audio_features(sys.argv[1])
    else:
        print(json.dumps({"error": "No audio file provided"}))