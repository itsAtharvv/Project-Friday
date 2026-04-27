import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# Load the model persistently once at startup
model = WhisperModel("tiny.en", device="cpu", compute_type="int8")

SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5      # record in 0.5s chunks
SILENCE_THRESHOLD = 0.005  # energy level below this = silence
SILENCE_CHUNKS = 2        # stop after 2 silent chunks (1 second of silence)
MAX_CHUNKS = 10           # max 5 seconds total

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

    # Transcribe directly from numpy array in memory, saving disk IO
    segments, _ = model.transcribe(audio, vad_filter=True)
    text = " ".join([segment.text for segment in segments]).strip()

    print(f"[STT] Heard: {text}")
    return text