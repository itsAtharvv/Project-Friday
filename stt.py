import whisper
import numpy as np
import sounddevice as sd
import tempfile
import os
import soundfile as sf

model = whisper.load_model("small")

SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5      # record in 0.5s chunks
SILENCE_THRESHOLD = 0.005  # energy level below this = silence
SILENCE_CHUNKS = 2        # stop after 2 silent chunks (1 second of silence)
MAX_CHUNKS = 10           # max 5 seconds total

def is_silent(chunk: np.ndarray) -> bool:
    return np.sqrt(np.mean(chunk**2)) < SILENCE_THRESHOLD

def listen():
    print("[STT] Listening...")

    chunks = []
    silent_count = 0
    speaking = False
    chunk_samples = int(SAMPLE_RATE * CHUNK_DURATION)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
        for _ in range(MAX_CHUNKS):
            chunk, _ = stream.read(chunk_samples)
            chunk = chunk.squeeze()
            energy = np.sqrt(np.mean(chunk**2))
            print(f"[STT] Energy: {energy:.4f}")
            chunks.append(chunk)

            if energy >= SILENCE_THRESHOLD:
                speaking = True
                silent_count = 0
            else:
                if speaking:
                    silent_count += 1

            if speaking and silent_count >= SILENCE_CHUNKS:
                print("[STT] Silence detected, processing...")
                break

    if not speaking:
        print("[STT] No speech detected, skipping...")
        return ""

    audio = np.concatenate(chunks)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, SAMPLE_RATE)
        tmp_path = f.name

    result = model.transcribe(tmp_path)
    os.remove(tmp_path)

    text = result["text"].strip()
    print(f"[STT] Heard: {text}")
    return text