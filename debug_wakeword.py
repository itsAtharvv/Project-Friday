"""
Run this directly to debug wakeword detection scores in real time.
Usage: .venv/bin/python debug_wakeword.py
"""
import sys
import sounddevice as sd
import numpy as np
import openwakeword
from openwakeword.model import Model

# Suppress onnxruntime warnings
import warnings
warnings.filterwarnings("ignore")

paths = openwakeword.get_pretrained_model_paths()
jarvis_path = [p for p in paths if "hey_jarvis" in p]
print(f"Model path: {jarvis_path}")

model = Model(wakeword_model_paths=jarvis_path)

# Use device 9 (sof-hda-dsp hw:1,7) which is natively 16kHz
DEVICE = 9

print(f"\nUsing device: {sd.query_devices(DEVICE)['name']}")
print("\nListening... Say 'hey jarvis' repeatedly and clearly.")
print("Scores above 0.0 will print. Threshold to trigger = 0.5\n")
print(f"{'Frame':<8} {'Score':<10} {'Bar'}")
print("-" * 40)

frame = 0
with sd.InputStream(samplerate=16000, channels=1, dtype='int16', blocksize=1280, device=DEVICE) as stream:
    while True:
        audio, overflowed = stream.read(1280)
        chunk = audio[:, 0] if audio.ndim == 2 else audio.flatten()
        pred = model.predict(chunk)
        score = float(max(pred.values())) if pred else 0.0
        frame += 1

        bar = "█" * int(score * 40)
        trigger = " <<< TRIGGERED!" if score > 0.5 else ""
        if score > 0.01 or frame % 50 == 0:
            print(f"{frame:<8} {score:<10.4f} {bar}{trigger}", flush=True)
        sys.stdout.flush()
