import sys
import numpy as np
import librosa
import noisereduce as nr
from pedalboard import Pedalboard, NoiseGate, Compressor, LowShelfFilter, Gain
from pedalboard.io import AudioFile
import soundfile as sf

def process_audio(input_file):
    sr = 44100  # Sample rate
    output_file = input_file.replace(".wav", "_enhanced.wav")

    # Read the audio file
    with AudioFile(input_file).resampled_to(sr) as f:
        audio = f.read(f.frames)

    # Advanced noise reduction
    reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=False, prop_decrease=0.9, n_fft=1024, hop_length=256)

    # Apply effects using Pedalboard
    board = Pedalboard([
        NoiseGate(threshold_db=-35, ratio=2.0, release_ms=200),
        Compressor(threshold_db=-20, ratio=3.0, attack_ms=10, release_ms=200),
        LowShelfFilter(cutoff_frequency_hz=300, gain_db=12, q=0.7),
        Gain(gain_db=8)
    ])
    effected = board(reduced_noise, sr)

    # Save the processed audio
    with AudioFile(output_file, 'w', sr, effected.shape[0]) as f:
        f.write(effected)

    return output_file

def analyze_audio(audio_path):
    try:
        # Load processed audio file
        y, sr = librosa.load(audio_path, sr=None)

        # Estimate pitch using YIN algorithm
        pitch_values = librosa.yin(y, fmin=50, fmax=500, sr=sr)
        pitch_values = pitch_values[~np.isnan(pitch_values)]
        avg_pitch = np.mean(pitch_values) if pitch_values.size > 0 else 0

        # Calculate amplitude (RMS)
        amplitude_value = np.sqrt(np.mean(y**2))

        # Calculate frequency spectrum (Mean Frequency)
        freqs = np.fft.rfftfreq(len(y), d=1/sr)
        spectrum = np.abs(np.fft.rfft(y))
        mean_frequency = np.sum(freqs * spectrum) / np.sum(spectrum) if np.sum(spectrum) > 0 else 0

        # Estimate tempo
        tempo_array, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo_value = float(tempo_array[0]) if tempo_array.size > 0 else 0

        # Validate tempo value
        if tempo_value < 40 or tempo_value > 240:  # Typical BPM range
            print(f"Warning: Invalid tempo value detected: {tempo_value}. Setting to 0.", file=sys.stderr)
            tempo_value = 0

        return avg_pitch, amplitude_value, mean_frequency, tempo_value
    except Exception as e:
        print(f"Error analyzing audio file {audio_path}: {e}", file=sys.stderr)
        return None, None, None, None
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_audio.py <input_file>")
        sys.exit(1)

    input_path = sys.argv[1]

    # Step 1: Enhance the audio
    enhanced_audio = process_audio(input_path)

    # Step 2: Extract pitch, amplitude, frequency, and tempo
    pitch_value, amplitude_value, mean_frequency, tempo_value = analyze_audio(enhanced_audio)

    # ✅ Output only the file path for Node.js to read properly
    print(enhanced_audio)

    # 🔹 Log pitch, amplitude, frequency & tempo separately
    print(f"Estimated Pitch (Hz): {pitch_value:.2f}", file=sys.stderr)
    print(f"Estimated Amplitude (RMS): {amplitude_value:.4f}", file=sys.stderr)
    print(f"Mean Frequency (Hz): {mean_frequency:.2f}", file=sys.stderr)
    print(f"Estimated Tempo (BPM): {tempo_value:.2f}", file=sys.stderr)
