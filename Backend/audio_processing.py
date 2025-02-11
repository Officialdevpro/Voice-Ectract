import sys
import os
import numpy as np
import noisereduce as nr
from pedalboard import *
from pedalboard.io import AudioFile
import soundfile as sf

def process_audio(input_file):
    sr = 44100  # Sample rate
    output_file = input_file.replace(".wav", "_enhanced.wav")

    # Read the audio file
    with AudioFile(input_file).resampled_to(sr) as f:
        audio = f.read(f.frames)

    # Apply noise reduction
    reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.75)

    # Apply effects using Pedalboard
    board = Pedalboard([
        NoiseGate(threshold_db=-30, ratio=1.5, release_ms=250),
        Compressor(threshold_db=-16, ratio=2.5),
        LowShelfFilter(cutoff_frequency_hz=400, gain_db=10, q=1),
        Gain(gain_db=10)
    ])
    effected = board(reduced_noise, sr)

    # Save the processed audio
    with AudioFile(output_file, 'w', sr, effected.shape[0]) as f:
        f.write(effected)

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_audio.py <input_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    enhanced_audio = process_audio(input_path)
    print(enhanced_audio)  # Print the output filename for the Node.js server
