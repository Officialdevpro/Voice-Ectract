import numpy as np
import librosa
import sys
import json

def extract_audio_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    
    if len(y.shape) > 1:
        y = librosa.to_mono(y)
    
    pitch, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    pitch = np.nanmean(pitch)
    pitch = round(float(pitch), 2) if not np.isnan(pitch) else None
    
    amplitude = round(float(np.sqrt(np.mean(y ** 2))), 4)
    
    fft_spectrum = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(len(y), 1 / sr)
    dominant_freq = freqs[np.argmax(fft_spectrum)]
    dominant_freq = round(float(dominant_freq), 2)
    
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = round(float(tempo.item()), 2) if np.isscalar(tempo) == False else round(float(tempo), 2)

    
    return {
        "pitch": pitch,
        "amplitude": amplitude,
        "dominant_frequency": dominant_freq,
        "tempo": tempo
    }

if __name__ == '__main__':
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
        try:
            features = extract_audio_features(audio_path)
            print(json.dumps(features))  # Print JSON result
        except Exception as e:
            print(json.dumps({"error": str(e)}))
    else:
        print(json.dumps({"error": "No audio file provided"}))
