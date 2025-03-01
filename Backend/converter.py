import numpy as np
import librosa
import sys
import json

def extract_audio_features(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)

        if len(y.shape) > 1:
            y = librosa.to_mono(y)

        pitch, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        pitch = np.nanmean(pitch)
        pitch = round(float(pitch), 2) if not np.isnan(pitch) else None

        amplitude = round(float(np.sqrt(np.mean(y ** 2))), 4)

        fft_spectrum = np.abs(np.fft.rfft(y))
        freqs = np.fft.rfftfreq(len(y), 1 / sr)
        dominant_freq = round(float(freqs[np.argmax(fft_spectrum)]), 2)

        tempo_array, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = round(float(tempo_array[0]), 2) if len(tempo_array) > 0 else None


        result = {
            "pitch": pitch,
            "amplitude": amplitude,
            "dominant_frequency": dominant_freq,
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
